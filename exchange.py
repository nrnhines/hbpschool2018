from neuron import h
pc = h.ParallelContext()
nhost = int(pc.nhost())
rank = int(pc.id())

mgcon = []
g_gids = [i for i in range(5+rank, 10, nhost)]
for m in range(rank, 5, nhost):
  for g in range(5, 10):
    mgcon.append((m, 0, 0, g, 0, 0))
print ("g_gids", g_gids)
print ("mgcon", mgcon)

#mgcon is list of (m, ms, mx, g, gs, gx) on this rank
#g_gids is a list of g's on this rank

# organize the tuples destined for rank g%nhost as  [tuple]
have = [[] for _ in range(nhost)]
for con in mgcon:
  g = con[3]
  have[g%nhost].append(con)

#rendezvous rank has all the g tuple
#such that thisrank = g%nhost
have = pc.py_alltoall(have)

#the want machine has a list of granule cell gids = [g]
# and wants all the tuples that refer to a g

#tell the rendezvous ranks what g's it wants
want = [[] for _ in range(nhost)]
for g in g_gids:
  want[g%nhost].append(g)

#rendezvous rank knows who is interested in g
want = pc.py_alltoall(want)
print ("want", want)

# create on rendezvous rank a dict of g -> destination rank
g2rank = {}
for r, gs in enumerate(want):
  for g in gs:
    g2rank[g] = r

#rendezvous rank sends back tuples to where the g exists
send = [[] for _ in range(nhost)]
for tuples in have:
  for t in tuples:
    g = t[3]
    send[g2rank[g]].append(t)
recv = pc.py_alltoall(send)

pc.barrier()
h.quit()
