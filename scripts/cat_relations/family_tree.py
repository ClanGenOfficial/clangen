# from graphviz import Digraph
# import pandas as pd
#
# ancestry = pd.read_csv('sample_ancestry.csv')
# earl_ans = ancestry.loc[ancestry['Relation'] == 'Earliest Ancestor', 'Cat 1'].iloc[0]
# ancestry['recorded_ind'] = 0    # Flag for saying cats whose data has been recorded in the tree
#
# incomp = [earl_ans]
# comp = []
#
# dot = Digraph(comment = 'Ancestry', graph_attr = {'splines':'ortho'})
# node_nm = []
#
# # Initializing first node
# det = str(ancestry.loc[ancestry['Cat 1'] == earl_ans, 'Details'][0])
# g = ancestry.loc[ancestry['Cat 1'] == earl_ans, 'Gender'][0]
# sh = 'rect' if g == 'M' else 'ellipse'
# dot.node(earl_ans, earl_ans, tooltip = det, shape = sh)
# node_nm.append(earl_ans)
#
# ancestry.loc[ancestry['Cat 1'] == earl_ans, 'recorded_ind'] = 1
#
# # max_iter should be greater than number of generations
# max_iter = 5
#
# for i in range(0, max_iter):
#     temp = ancestry[ancestry['recorded_ind'] == 0]
#
#     if len(temp) == 0:      # Break loop when all individuals have been recorded
#         break
#     else:
#         temp['this_gen_ind'] = temp.apply(lambda x: 1 if x['Cat 2'] in incomp else 0, axis = 1)
#
#         # Spouse Relationship
#         this_gen = temp[(temp['this_gen_ind'] == 1) & (temp['Relation'] == 'Spouse')]
#         if len(this_gen) > 0:
#             for j in range(0, len(this_gen)):
#                 per1 = this_gen['Cat 1'].iloc[j]
#                 per2 = this_gen['Cat 2'].iloc[j]
#                 det = str(this_gen['Details'].iloc[j])
#                 g = this_gen['Gender'].iloc[j]
#                 sh = 'rect' if g == 'M' else 'ellipse'
#                 with dot.subgraph() as subs:
#                     subs.attr(rank = 'same')
#                     subs.node(per1, per1, tooltip = det, shape = sh, fillcolor = "red")
#                     node_nm.append(per1)
#                     subs.edge(per2, per1, arrowhead = 'none', color = "black:invis:black")
#
#         # Kitten Relationship
#         this_gen = temp[(temp['this_gen_ind'] == 1) & (temp['Relation'] == 'Child')]
#         if len(this_gen) > 0:
#             for j in range(0, len(this_gen)):
#                 per1 = this_gen['Cat 1'].iloc[j]
#                 per2 = this_gen['Cat 2'].iloc[j]
#                 det = str(this_gen['Details'].iloc[j])
#                 g = this_gen['Gender'].iloc[j]
#                 sh = 'rect' if g == 'M' else 'ellipse'
#                 dot.node(per1, per1, tooltip = det, shape = sh)
#                 node_nm.append(per1)
#                 dot.edge(per2, per1)
#
#         comp.extend(incomp)
#         incomp = list(temp.loc[temp['this_gen_ind'] == 1, 'Cat 1'])
#         ancestry['recorded_ind'] = temp.apply(lambda x: 1 if (x['Cat 1'] in incomp) | (x['Cat 1'] in comp) else 0, axis = 1)
#
# dot.format = 'svg'
# dot.render('sample_ancestry.gv.svg', view = True)