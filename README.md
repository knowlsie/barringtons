## Barrington's

Have you ever wanted to compute the majority vote among 13 bits...? Have you ever wanted to do that using 562,036,736 members of your favorite not solvable group (aka S5)...? Now you can with this repo, guaranteed to be the slowest non-trivial implementation of MAJ13 on Github!

Jokes-aside, this is a extremely rushed and horribly memory-inefficient implementation of Barrington's theorem (which converts circuits into "group programs"), including a simple builder of circuits for MAJ-k. It's mostly intended as a proof by example, rather than anything practical. (Technically, the implemented conversion of MAJ-k into a circuit is too deep to fulfill Barrington's Theorem's conditions, but the correct one has terrible constants.) 

The group program conversion should work (albeit not especially quickly) for generic circuits implemented with AND, OR and NOT gates, beyond just MAJ-k. So this effectively allows you to do generic circuit computation using just a few group elements!