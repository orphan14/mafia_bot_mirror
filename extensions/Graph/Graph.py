import networkx as nx

class MatchGraph:

  def __init__(self, queue, matchups):
    self.match_graph = nx.Graph()
#    self.idToUsername = {}
#    self.usernameToId = {}
    self.idToMinWeight = {}
    self.idToNodeAndWeight = {}
    self.idPaired = {}
    self.edgeToWeight = {}
    self.player_combos = []
    self.player_list = []
    for player in queue:
      # Add node for every player
      self.match_graph.add_nodes_from([player.mUserId])
#      self.idToUsername[player.mId] = player.mDiscordUsername
#      self.usernameToId[player.mDiscordUsername] = player.mId
      self.player_list.append(player.mUserId)
    print("created player list...")
    for x in self.all_pairs_in_queue(self.player_list):
      self.player_combos.append(x)
    print("created player combos...")
    # First go through matchups to make weights between players take the min
    matchup_dict = {}
    for matchup in matchups:
      userId = matchup.mUserId
      opponentId = matchup.mOpponentUserId
      weight = 1000 #default to 1000 games if they have never played each other
      if matchup.mGamesSinceLast is not None:
        weight = matchup.mGamesSinceLast
      if(matchup_dict.get((opponentId,userId))):
        matchup_dict[(userId,opponentId)] = min(weight,matchup_dict[(opponentId,userId)])
        matchup_dict[(opponentId,userId)] = min(weight,matchup_dict[(opponentId,userId)])
      else:
        matchup_dict[(userId,opponentId)] = weight
    print("created matchup dict...")
    max_weight=1000;
    try:
      max_weight = max(p for p in matchup_dict.values() if p < 1000)
    except:
      #this can only happen is all values are 1000 or if there is only 1 user to pair.
      max_weight = 1
    for matchup in matchup_dict:
      if 1000 == matchup_dict[matchup]:
        matchup_dict[matchup] = max_weight+1 #Do this to make weights in ballpark of each other
      userId = matchup[0]
      opponentId = matchup[1]
      weight = matchup_dict[matchup]
      self.match_graph.add_weighted_edges_from([(userId,opponentId,weight)],"weight")
      if not (self.edgeToWeight.get((opponentId,userId))):
        self.edgeToWeight[(userId,opponentId)] = weight;
    self.edgeToWeightDesc = sorted(self.edgeToWeight.items(), key=lambda key_val: key_val[1],reverse=True)
    self.edgeToWeightAsc = sorted(self.edgeToWeight.items(), key=lambda key_val: key_val[1])
    print(self.edgeToWeightAsc)
    print(self.edgeToWeightDesc)

  def all_pairs_in_queue(self,player_id_list):
    if len(player_id_list) < 2:
      yield []
      return
    if len(player_id_list) % 2 == 1:
      # Handle odd length list
      for i in range(len(player_id_list)):
        for result in self.all_pairs_in_queue(player_id_list[:i] + player_id_list[i + 1:]):
          yield result
    else:
      a = player_id_list[0]
      for i in range(1, len(player_id_list)):
        pair = (a, player_id_list[i])
        for rest in self.all_pairs_in_queue(player_id_list[1:i] + player_id_list[i + 1:]):
          yield [pair] + rest

  def all_edge_combos(self,edgeToWeightDict,paired):
    if len(edgeToWeightDict) < 2:
      yield []
      return
    if len(edgeToWeightDict) % 2 == 1:
      # Handle odd length list
      for i in range(len(edgeToWeightDict)):
        for result in self.all_edge_combos(edgeToWeightDict[:i] + edgeToWeightDict[i + 1:],paired):
          yield result
    else:
      a = edgeToWeightDict[0]
      print(f"Adding combos for edge {a}")
      for i in range(1, len(edgeToWeightDict)):
        for rest in self.all_edge_combos(edgeToWeightDict[1:i] + edgeToWeightDict[i + 1:],paired):
            if (a[0][0] not in paired and a[0][1] not in paired):
              paired.append(a[0][0])
              paired.append(a[0][1])
              print(f"a:{a}")
              yield [a] + rest
            else:
              print(f"rest:{rest}")
              yield rest


  def try_to_pair(self):
    print(len(self.match_graph.edges(1)))

  def find_edge_combos(self):
    combos = []
    for edge in self.edgeToWeightDesc:
      paired = []
#      for inner_edge in self.edgeToWeightDesc:

  def remove_edge_pair(self):
    #self.try_to_pair()
    combos=[]
    for x in self.all_edge_combos(self.edgeToWeightAsc,[]):
      combos.append(x)
    print(combos)
#    for edge in self.edgeToWeightAsc:



  def brute_force_pair(self):
    edgeToWeight = {}
    for id in self.player_list:
      for edge in nx.edges(self.match_graph, id):
        edgeToWeight[edge] = nx.path_weight(self.match_graph, list(edge), "weight")

    pairings_score = []
    for a_pairing in self.player_combos:
      cumulative_score=0
      for pair in a_pairing:
        if 0 == edgeToWeight[pair]:
          cumulative_score=0
          break;
        else:
          cumulative_score+=edgeToWeight[pair]
      pairings_score.append(cumulative_score)
    index_max = max(range(len(pairings_score)), key=pairings_score.__getitem__)
    pairing=[]
    for final_pairing in self.player_combos[index_max]:
      pairing.append(((final_pairing),edgeToWeight[final_pairing]))
    return pairing

  def clean(self):
    self.idToUsername = {}
    self.usernameToId = {}
    self.idToMinWeight = {}
    self.idToNodeAndWeight = {}
    self.idPaired = {}
    self.player_combos = []
    self.player_list = []
