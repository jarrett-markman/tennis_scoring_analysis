# Code for first step analysis visual and ggplot
# Load libraries
library(tidyverse)
library(DiagrammeR)
library(DiagrammeRsvg)
library(webshot)
# Create decision tree labels
labels <- c("Deuce", "Advantage Server", "Advantage Returner", "Game Server", "Game Returner")
# Create a nodes data frame
nodes <- data.frame(id = labels, label = labels)
# Create the graph from DiagrammeR package
graph <- create_graph() %>% 
  # Add graph attributes
  add_global_graph_attrs("layout", "dot", "graph") %>%
  add_global_graph_attrs("concentrate", "true", "graph") %>%
  add_nodes_from_table(
    table = nodes,
    label_col = label) %>% 
  # Add col. lines from transitioning states
  add_edge(from = "Deuce", to = "Advantage Server") %>% 
  add_edge(to = "Deuce", from = "Advantage Server") %>%
  add_edge(from = "Deuce", to = "Advantage Returner") %>% 
  add_edge(to = "Deuce", from = "Advantage Returner") %>%
  add_edge(from = "Advantage Server", to = "Game Server") %>% 
  add_edge(from = "Advantage Returner", to = "Game Returner") %>%
  # Absorbing states
  add_edge(from = "Game Server", to = "Game Server") %>% add_edge(from = "Game Returner", to = "Game Returner") %>%
  set_edge_attrs(
    edge_attr = "label",
    values = c("x", "1 - x", "1 - x", "x", "x", "1 - x", 1, 0)
  ) %>%
  select_nodes_by_id(nodes = 1:length(labels)) %>% 
  # Order node attributes
  set_node_attrs(node_attr = "fixedsize", values = FALSE) %>% 
  set_node_attrs_ws(
    node_attr = shape,
    value = "rectangle") %>% 
  # Change colors
  set_node_attrs_ws(
    node_attr = "color",
    value = "black"
  ) %>%
  set_node_attrs(
    node_attr = "fillcolor",
    value = "white"
  ) %>%
  clear_selection() 
# Display graph
render_graph(graph, width = 750, height = 300)
# Save visuals
export_graph(graph, file_name = "Tree Diagram.svg", file_type = "svg")
webshot(url = "url", file = "Tree Diagram.png")
