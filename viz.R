# Libraries
library(readxl)
library(tidyverse)
library(gt)
library(httr)
library(rvest)
# Get atp headshots
# Store url for rankings page
url <- "https://www.atptour.com/en/rankings/singles"
# GET response and read html
response <- GET(url)
html <- read_html(response)
# Follow path via inspect element
atp_ids <- html %>% html_nodes(".container > .wrapper > .atp_layout > .atp_layout-container >             
             .atp_layout-content > .atp_rankings-all > .mobile-table") %>%  
  # Get anchored elements and find href names and ids
  html_nodes("a") %>%  html_attr("href") %>%  
  # Remove values from player urls
  str_remove("/en/players/") %>%  
  str_remove("/overview") %>%  
  str_remove("/rankings-breakdown?team=singles") %>%  
  unlist() %>% 
  as.data.frame() %>%  
  filter(!grepl("rankings", .) & . != "#") %>%  
  as.vector() %>%  
  unlist()
# Split ids vector into player and id columns
atp <- strsplit(atp_ids, "/") %>% as.data.frame() %>% t() %>% as.data.frame()
colnames(atp) <- c("player", "id")
rownames(atp) <- 1:nrow(atp)
atp <- atp %>% mutate(player = gsub("-", " ", player))
atp$player <- tools::toTitleCase(atp$player) # Use toTitleCase to capitalize player names
atp$headshot_url <- paste0("https://www.atptour.com/-/media/alias/player-headshot/", atp$id)
# Get wta ids from espn
url <- "https://www.espn.com/tennis/rankings/_/type/wta"
response <- GET(url)
html <- read_html(response)
wta <- html %>% 
  html_nodes(".Wrapper") %>% 
  html_nodes("a") %>% html_attr("href") %>% 
  str_subset("/tennis/player") %>%
  str_remove("https://www.espn.com/tennis/player/_/id/") %>%
  as.vector()
# Split ids vector into player and id columns
wta <- strsplit(wta, "/") %>% as.data.frame() %>% t() %>% as.data.frame()
colnames(wta) <- c("id", "player")
rownames(wta) <- 1:nrow(wta)
wta <- wta %>% mutate(player = gsub("-", " ", player)) # Replace - with " "
wta$player <- tools::toTitleCase(wta$player)
# Iterate ids over espn url for player headshots
wta <- wta %>%
  mutate(
    headshot_url = paste0("https://a.espncdn.com/combiner/i?img=/i/headshots/tennis/players/full/", id,".png&w=350&h=254")
  )
# Read in modified csv as excel  
data <- read_excel("Results.xlsx")
### VIZ 1 - "Accuracy" by scoring system 
viz1 <- data %>%
  group_by(Scoring, `Best of`) %>%
  summarise(
    accurate = sum(`Accurate?`),
    n = n(),
    accuracy = accurate/n
  ) %>%
  ungroup() %>%
  ggplot(aes(x = reorder(paste(`Best of`, "Sets", Scoring), accuracy), y = accuracy, fill = reorder(paste(`Best of`, "Sets", Scoring), accuracy))) +
  geom_bar(stat = "identity") +
  theme_bw() +
  labs(x = "Scoring", y = "Accuracy",
       title = "Accuracy by Scoring System",
       subtitle = 'An "accurate" match is one simulated match that results in the same expected result as 100 grand slam simulated matches',
       caption = "Jarrett Markman") +
  theme(plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
        plot.subtitle = element_text(hjust = 0.5),
        legend.position = "none") 
# No huge difference for each match - 5 sets most "accurate"
# Manually find index for men's and women's data
data[522896:nrow(data), 15] = "WTA" # Create new column for league
data[1:522895, 15] = "ATP"
data <- data %>% rename(league = ...15) # Change colname
# Create cols for men's and women's p1 and p2's to aggregate player results
men_p1 <- data %>% 
  filter(league == "ATP") %>% 
  select(player = `Player 1`, `Best of`, Scoring, `Winning Player`, Surface, gs_wp = `Player 1 Grand Slam Match Win Probability (100 Sims)`)
men_p2 <- data %>% 
  filter(league == "ATP") %>% 
  select(player = `Player 2`, `Best of`, Scoring, `Winning Player`, Surface, gs_wp = `Player 2 Grand Slam Match Win Probability (100 Sims)`)
wom_p1 <- data %>% 
  filter(league == "WTA") %>% 
  select(player = `Player 1`, `Best of`, Scoring, `Winning Player`, Surface, gs_wp = `Player 1 Grand Slam Match Win Probability (100 Sims)`)
wom_p2 <- data %>% 
  filter(league == "WTA") %>% 
  select(player = `Player 2`, `Best of`, Scoring, `Winning Player`, Surface, gs_wp = `Player 2 Grand Slam Match Win Probability (100 Sims)`)
mens_ovr <- bind_rows(men_p1, men_p2)
wom_ovr <- bind_rows(wom_p1, wom_p2)
### VIZ 2 - Top men's players
# First get overall win percentage in all matches simulated ("played")
mens_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% ungroup() %>%
  select(player, overall_win_pct = win_pct, total_matches_played = n) -> mens_ovr_wr
# Aggregate win percentages by `Best of` and Scoring by player for their win rates in each sequence
viz2 <- mens_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% 
  ungroup() %>%
  # Transpose columns from sets and scoring based on each player
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "win_pct_",
              values_from = win_pct) %>%
  # Join atp headshots and overall win rates
  left_join(atp, by = "player") %>% 
  left_join(mens_ovr_wr, by = "player") %>%
  select(-id) %>% # Remove player id
  arrange(desc(overall_win_pct)) %>% # Arrange highest-lowest
  # Create rank col. and order columns
  mutate(rank = row_number()) %>%
  select(rank, player, headshot_url, total_matches_played, overall_win_pct, win_pct_5_ad, `win_pct_5_no-ad`, win_pct_3_ad, `win_pct_3_no-ad`) %>% 
  head(20) %>% # Get first 20 observations
  gt() %>%
  gtExtras::gt_img_rows(headshot_url) %>%
  gtExtras::gt_theme_538() %>%
  cols_label( # Change colnames
    headshot_url = "",
    total_matches_played = "Total Matches Played",
    overall_win_pct = "Total Match Win %",
    win_pct_5_ad = "Win % in Best of 5 Sets (ad)",
    `win_pct_5_no-ad` = "Win % in Best of 5 Sets (no-ad)",
    win_pct_3_ad = "Win % in Best of 3 Sets (ad)",
    `win_pct_3_no-ad` = "Win % in Best of 3 sets (no-ad)"
  ) %>%
  data_color( # Create color scale for columns 5-9 (all win pct cols. )
    columns = c(5:9), palette = scales::col_numeric("PRGn", domain = NULL)
  ) %>%
  cols_align(align = "center") %>% # Center cols
  tab_header(title = "Top 20 ATP Players (Based on Overall Match Win %)",
             subtitle = "Based on match simulations") %>%
  tab_source_note(source_note = "Jarrett Markman") %>%
  tab_options(table.width = pct(90))
### Viz 3 - Top women's players
# Repeat same code, apply to wom_ovr instead
wom_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% ungroup() %>%
  select(player, overall_win_pct = win_pct, total_matches_played = n) -> wom_ovr_wr
viz3 <- wom_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% 
  ungroup() %>%
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "win_pct_",
              values_from = win_pct) %>%
  left_join(wta, by = "player") %>% 
  left_join(wom_ovr_wr, by = "player") %>%
  select(-id) %>%
  arrange(desc(overall_win_pct)) %>%
  mutate(rank = row_number()) %>%
  select(rank, player, headshot_url, total_matches_played, overall_win_pct, win_pct_5_ad, `win_pct_5_no-ad`, win_pct_3_ad, `win_pct_3_no-ad`) %>% 
  head(20) %>%
  gt() %>%
  gtExtras::gt_img_rows(headshot_url) %>%
  gtExtras::gt_theme_538() %>%
  cols_label(
    rank = "",
    headshot_url = "",
    total_matches_played = "Total Matches Played",
    overall_win_pct = "Total Match Win %",
    win_pct_5_ad = "Win % in Best of 5 Sets (ad)",
    `win_pct_5_no-ad` = "Win % in Best of 5 Sets (no-ad)",
    win_pct_3_ad = "Win % in Best of 3 Sets (ad)",
    `win_pct_3_no-ad` = "Win % in Best of 3 sets (no-ad)"
  ) %>%
  data_color(
    columns = c(5:9), palette = scales::col_numeric("PRGn", domain = NULL)
  ) %>%
  cols_align(align = "center") %>%
  tab_header(title = "Top 20 WTA Players (Based on Total Match Win %)",
             subtitle = "Based on match simulations") %>%
  tab_source_note(source_note = "Jarrett Markman") %>%
  tab_options(table.width = pct(90))
# Get expected match win percentage by scoring system (over 100 gs sims)
mens_a <- mens_ovr %>% select(player, `Best of`, Scoring, gs_wp) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(x_wins = sum(gs_wp),
            matches = n(),
            x_match_wp = x_wins/matches
            ) %>% arrange(desc(x_match_wp)) %>%
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "x_match_wp_",
              values_from = x_match_wp)
# Get expected match win percentages by scoring system
mens_b <- mens_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% 
  ungroup() %>%
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "win_pct_",
              values_from = win_pct) 
mens_df <- inner_join(mens_a, mens_b, by = c("player")) %>% # Join data frames together and select expected & actual win pct results
  select(player, 
         x_match_wp_5_ad, win_pct_5_ad, `x_match_wp_5_no-ad`, `win_pct_5_no-ad`, 
         x_match_wp_3_ad, win_pct_3_ad, `x_match_wp_3_no-ad`, `win_pct_3_no-ad`)
m_diff_df <- mens_df %>%
  summarise( # Calculate difference b/w simulations and exp. result 
    "5 Sets, Ad" = x_match_wp_5_ad - win_pct_5_ad,
    "5 Sets, No-ad" = `x_match_wp_5_no-ad` - `win_pct_5_no-ad`,
    "3 Sets, Ad" = x_match_wp_3_ad - win_pct_3_ad,
    "3 Sets, No-ad" = `x_match_wp_3_no-ad` - `win_pct_3_no-ad`
  ) %>% 
  pivot_longer(cols = !player, names_to = "condition", values_to = "difference")
m_diff_df$condition <- factor(m_diff_df$condition, levels = c("5 Sets, Ad", "5 Sets, No-ad", "3 Sets, Ad", "3 Sets, No-ad"))
# Viz 4 - Boxplot
viz4 <- ggplot(m_diff_df, aes(x = condition, y = difference, fill = condition)) +
  geom_boxplot() +
  labs(x = "Scoring System", y = "Expected - Actual Win Percentage",
       title = "Boxplot Distribution of Variance in Win Percentages in Men's Matches",
       caption = "Jarrett Markman") +
  theme_bw() +
  theme(plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
        plot.subtitle = element_text(size = 8, hjust = 0.5),
        legend.position = "none")
# Get the variance for the differences in expected and actual win pct for each scoring system
m_diff_vars <- mens_df %>%
  summarise(
    diff_5_ad = x_match_wp_5_ad - win_pct_5_ad,
    diff_5_no_ad = `x_match_wp_5_no-ad` - `win_pct_5_no-ad`,
    diff_3_ad = x_match_wp_3_ad - win_pct_3_ad,
    diff_3_no_ad = `x_match_wp_3_no-ad` - `win_pct_3_no-ad`
  ) %>%
  summarise(
    var_diff_5_ad = var(diff_5_ad, na.rm = TRUE),
    var_diff_5_no_ad = var(diff_5_no_ad, na.rm = TRUE),
    var_diff_3_ad = var(diff_3_ad, na.rm = TRUE),
    var_diff_3_no_ad = var(diff_3_no_ad, na.rm = TRUE)
  )
# Transpose the diff_vars data frame
m_transposed_diff_vars <- as.data.frame(t(m_diff_vars))
m_transposed_diff_vars$condition <- rownames(m_transposed_diff_vars)
m_var_data <- m_transposed_diff_vars %>%
  mutate(scoring_system = ifelse(grepl("no", condition), "no-ad", "ad"),
         condition = ifelse(grepl("5", condition), 5, 3)) %>%
  reframe(x = paste(condition, "Sets", scoring_system), y = V1)
rownames(m_var_data) <- 1:nrow(m_var_data)
# Make a barplot with the data
# Viz 5 - barplot of variance
viz5 <- m_var_data %>%
  ggplot(aes(x = reorder(x, y), y = y, fill = reorder(x, y))) +
  geom_bar(stat = "identity") +
  labs(
    x = "Scoring System", y = "Variance",
    title = "Variance by Scoring System in Men's Matches",
    subtitle = "Variance measured on the difference between expected and actual win percentage",
    caption = "Jarrett Markman"
  ) +
  theme_bw() +
  theme(
    plot.title = element_text(size = 12, face = "bold", hjust = .5),
    plot.subtitle = element_text(hjust = 0.5),
    legend.position = "none"
  )
# Repeat code for woms_ovr
# Get expected match win percentage by scoring system (over 100 gs sims)
wom_a <- wom_ovr %>% select(player, `Best of`, Scoring, gs_wp) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(x_wins = sum(gs_wp),
            matches = n(),
            x_match_wp = x_wins/matches
  ) %>% arrange(desc(x_match_wp)) %>%
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "x_match_wp_",
              values_from = x_match_wp)
# Get expected match win percentages by scoring system
wom_b <- wom_ovr %>% mutate(win = ifelse(player == `Winning Player`, 1, 0)) %>%
  group_by(player, `Best of`, Scoring) %>%
  summarise(
    wins = sum(win),
    n = n(),
    win_pct = round(wins/n * 100, digits = 2)
  ) %>% 
  ungroup() %>%
  pivot_wider(names_from = c(`Best of`, Scoring), 
              id_cols = player,
              names_sep = "_", 
              names_prefix = "win_pct_",
              values_from = win_pct) 
wom_df <- inner_join(wom_a, wom_b, by = c("player")) %>% # Join data frames together and select expected & actual win pct results
  select(player, 
         x_match_wp_5_ad, win_pct_5_ad, `x_match_wp_5_no-ad`, `win_pct_5_no-ad`, 
         x_match_wp_3_ad, win_pct_3_ad, `x_match_wp_3_no-ad`, `win_pct_3_no-ad`)
w_diff_df <- wom_df %>%
  summarise( # Calculate difference b/w simulations and exp. result 
    "5 Sets, Ad" = x_match_wp_5_ad - win_pct_5_ad,
    "5 Sets, No-ad" = `x_match_wp_5_no-ad` - `win_pct_5_no-ad`,
    "3 Sets, Ad" = x_match_wp_3_ad - win_pct_3_ad,
    "3 Sets, No-ad" = `x_match_wp_3_no-ad` - `win_pct_3_no-ad`
  ) %>% 
  pivot_longer(cols = !player, names_to = "condition", values_to = "difference")
w_diff_df$condition <- factor(w_diff_df$condition, levels = c("5 Sets, Ad", "5 Sets, No-ad", "3 Sets, Ad", "3 Sets, No-ad"))
# Viz 6 - Boxplot
viz6 <- ggplot(w_diff_df, aes(x = condition, y = difference, fill = condition)) +
  geom_boxplot() +
  labs(x = "Scoring System", y = "Expected - Actual Win Percentage",
       title = "Boxplot Distribution of Variance in Win Percentages in Men's Matches",
       caption = "Jarrett Markman") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        plot.title = element_text(size = 12, face = "bold", hjust = 0.5),
        plot.subtitle = element_text(size = 8, hjust = 0.5),
        legend.position = "none")
# Get the variance for the differences in expected and actual win pct for each scoring system
w_diff_vars <- wom_df %>%
  summarise(
    diff_5_ad = x_match_wp_5_ad - win_pct_5_ad,
    diff_5_no_ad = `x_match_wp_5_no-ad` - `win_pct_5_no-ad`,
    diff_3_ad = x_match_wp_3_ad - win_pct_3_ad,
    diff_3_no_ad = `x_match_wp_3_no-ad` - `win_pct_3_no-ad`
  ) %>%
  summarise(
    var_diff_5_ad = var(diff_5_ad, na.rm = TRUE),
    var_diff_5_no_ad = var(diff_5_no_ad, na.rm = TRUE),
    var_diff_3_ad = var(diff_3_ad, na.rm = TRUE),
    var_diff_3_no_ad = var(diff_3_no_ad, na.rm = TRUE)
  )
# Transpose the diff_vars data frame
w_transposed_diff_vars <- as.data.frame(t(w_diff_vars))
w_transposed_diff_vars$condition <- rownames(w_transposed_diff_vars)
w_var_data <- w_transposed_diff_vars %>%
  mutate(scoring_system = ifelse(grepl("no", condition), "no-ad", "ad"),
         condition = ifelse(grepl("5", condition), 5, 3)) %>%
  reframe(x = paste(condition, "Sets", scoring_system), y = V1)
rownames(w_var_data) <- 1:nrow(w_var_data)
# Make a barplot with the data
# Viz 7 - barplot of variance
viz7 <- w_var_data %>%
  ggplot(aes(x = reorder(x, y), y = y, fill = reorder(x, y))) +
  geom_bar(stat = "identity") +
  labs(
    x = "Scoring System", y = "Variance",
    title = "Variance by Scoring System in Women's Matches",
    subtitle = "Variance measured on the difference between expected and actual win percentage",
    caption = "Jarrett Markman"
  ) +
  theme_bw() +
  theme(
    plot.title = element_text(size = 12, face = "bold", hjust = .5),
    plot.subtitle = element_text(hjust = 0.5),
    legend.position = "none"
  )
# Save all visuals
ggsave("Accuracy by Scoring System.png", viz1)
gtsave(viz2, "ATP Table.png")
gtsave(viz3, "WTA Table.png")
ggsave("ATP Boxplot.png", viz4)
ggsave("ATP Variance Bar Chart.png", viz5)
ggsave("WTA Boxplot.png", viz6)
ggsave("WTA Variance Bar Chart.png", viz7)