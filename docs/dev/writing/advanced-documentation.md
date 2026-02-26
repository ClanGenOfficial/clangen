# Advanced documentation

!!! todo "TODO"
    success in depth

!!! todo "TODO"
    hunting filtering in depth


!!! tip
    Hunting patrols have an additional level of filtering active above the patrol weights. First the game decides what prey reward the patrol should give (based on chances that change depending on the biome and season), and then, from the patrols that give that prey reward _as a non-stat success_, the acceptable patrols are weighed against each other. This naturally makes patrols that give huge prey rewards rare, no matter how many of those patrols you write. Don't worry about weighing hunting patrols according to their prey reward. Instead make each hunting patrol give roughly the same prey reward for all non-stat successes. The hunting filtering code will make sure the appropriate amount of prey is given. 

## Success chance calculation:

The success chance is roughly equivalent to the percentage chance of the patrol succeeding. However, this rate is modified by a number of different effects.

* Having a cat with a win skill/trait will raise the success rate by a base of 10. If the win skill is a 2nd level skill (i.e. great hunter, very smart, great speaker, ect) then an additional 5 is added.  If the win skill is a 3rd level skill (i.e. fantastic hunter, extremely smart, ect) then an additional 10 is added.  So, an excellent fighter could boost the success rate by 20 in total.
* Having a cat with a fail skill/trait will lower the success rate by 15
From there, the success rate is modified by the number of cats in the patrol and their exp.  
* The formula for this is (1 + 0.10 * len(self.patrol_cats)) * self.patrol_total_experience / (len(self.patrol_cats) * gm_modifier * 2).  
To explain what that means to someone without coding knowledge:
* (1 + 0.10 * len(self.patrol_cats)) << this is multiplying the number of cats on the patrol by .10 and then adding 1. 
* self.patrol_total_experience / (len(self.patrol_cats) * gm_modifier * 2) << this is finding the average of the cats' EXP and then multiplying it by the game mode modifier (this helps determine the difficulty of the game mode) and then multiplying it again by 2.
* The two numbers are then multiplied together and added to the success rate<br>
Then, a random number is rolled between 0 and 120.  If that number is below the success rate, yay! The patrol succeeds! If it's higher, then the patrol fails.  
* Success rates are capped at 90 when EXP is added, and then capped again at 115 when win skill/trait modifiers are added.  So that means, no matter what, there will always be a teeny tiny chance of failure even with the best possible combination of cats.  It also means that you should not give your patrol a success rate higher than 90, and, honestly, should try to avoid giving anything higher than 80.

