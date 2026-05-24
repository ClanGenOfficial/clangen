The Points of Interest system adds more depth to each Clan's territory by giving them a randomized gathering place, moonplace, and three discoverable locations in their territory that serve as points of interest to be mentioned in patrols and short events. This project helps make Clans feel even more unique to each other.

Disclaimer: Points of Interest do <b>not</b> use exclusionary tags.

## Creating a Point of Interest

New points of interest can be created in resources/dicts/points_of_interest.json. They use the following format:

~~~     
    "ID": {
        "category": "",
        "biome": [""],
        "tags": []
    }
~~~

The ID should be formatted as the category it is and a term to describe the location itself. For example: `gathering_meteor` is a gathering place most defined by a meteor crater. 

Biomes are listed the same way they are for short events and patrols, by using the biome's name in quotation marks or "any".

Options for categories and tags are listed in [categories and tags](#categories-and-tags) below, each should be within quotation marks with a comma between them (if necessary).

Here is an example of how a Point of Interest is coded.

~~~
    "moon_meteor": {
        "category": "moonplace",
        "biome": ["any"],
        "tags": []
    }
~~~

After adding a Point of Interest to their dicts file, it must also be added to `resources/lang/en/points_of_interest.en.json`. This allows you to determine what the Point of Interest is displayed as in game.

It is formatted as such:

~~~
"ID": "display name",
~~~

Here are some examples of what a completed version looks like:

~~~
"gather_fourtrees": "Fourtrees",
"moon_pool": "the Moonpool",
"terrain_deepforest": "the deep forest",
~~~

Gathering locations and Moonplaces should be capitalized and written as a proper noun. Terrain features can be a named location, ie: Sunning Rocks, or can be a brief description such as "a copse of aspen trees"

Keep in mind that a display name should either be a proper noun, or begin with "the" or "a/an" so it can easily be integrated into Short Events and Patrols. 

## Categories and Tags
### Categories

Points of Interest are distributed into three categories. Each Territory has randomly generated Points of Interest in each category.

|  Category |                                                                                            Description                                                                                           |
|:---------:|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------:|
| gathering | This is the Clan's Gathering place, where they interface with other Clans. One exists per territory.                                                                                             |
| moonplace | This is the Clan's moon place, where medicine cats meet once a moon. One exists per territory. It typically features some connection to the moon, stars, or night sky. One exists per territory. |
| territory | This is a feature within the Clan's territory that is notable due to either its appearance or opportunities around it. Three can be discovered per territory.                                    |

### Tags 
Points of Interests can use many different tags that denote circumstances around them to help specify how it can be used and what events/patrols it would fit with.

|        Tag        |                                                           Description                                                           |
|:-----------------:|:-------------------------------------------------------------------------------------------------------------------------------:|
|       cave        |                                                  a natural underground hollow.                                                  |
|      covered      |                                       any location that offers shelter from the elements.                                       |
|     fall_risk     |                                                 risk of heights-related injury.                                                 |
|       hole        |                                                     a cavity in the earth.                                                      |
|       prey        |                     anything the Clan hunts. Has multiple more specific tags. Should not be used together.                      |
|    prey:flying    |                                                 any prey that primarily flies.                                                  |
|    prey:water     |                                  prey found in or around water. assume your cats will get wet.                                  |
|    prey:ground    |                                                      ground-dwelling prey.                                                      |
|       rocks       |                                   feature that primarily includes rocks, boulders, or stone.                                    |
|      tainted      |                                  carries a risk of injury or illness due to unsafe conditions                                   |
|       trees       |                                                       incorporates trees.                                                       |
|      Twolegs      |                revolves around Twolegs. Has more specific tags. Should not be used alongside other twoleg tags.                 |
| Twolegs:abandoned |                    An object, structure, area created or modified by Twolegs that has since been abandoned.                     |
|  Twolegs:present  |                   An object, structure, area created or modified by Twolegs that has regular Twoleg activity.                   |
|     unstable      | If there is a potential for the structure to collapse in some way, unstable ceilings, unstable ground, an old tree branch, etc. |
|       water       |                  revolves around water. Has more specific tags. Should not be used alongside other water tags.                  |
|    water:still    |                              still bodies of water such as lakes, ponds, and some areas of marshes                              |
|   water:flowing   |                                              streams, rivers, rills, deltas, etc.                                               |
|    water:ocean    |                                                large saltwater bodies of water.                                                 |

## Using Points of Interest

### Constraints

Patrols and Short Events now have an additional constraint that can be utilized to include either a specific Point of Interest ID or tag. 

You can add this to any short event or patrol to constrain by Point of Interest. However, remember to constrain either via names or by a single tag, but not by both at once.

~~~
"poi": {
    "name": ["name"]
    "tags": ["tag"]
    }
~~~

## Using the Point Of Interest in a Sentence

Using a system similar to pronoun tags, Points of Interests can be mentioned in Short Events or Patrols with {POI} followed by relevant information; either the Points of Interest's IDs, or tags for a pool of Points of Interest.

A Point of Interest can either contain multiple names, separated by commas OR a single tag. Multiple tags cannot be used, nor should you mix tags and names.

A few examples below:

~~~
{POI/name/moon_pool,moon_cave,gather_monster}
{POI/tag/prey:fish}
~~~

Using one in a sentence should appear like this in the event itself versus the displayed result:

>Fluffy visits {POI/name/moon_pool} to commune with other medicine cats.

>Fluffy visits the Moonpool to commune with other medicine cats.

For this reason, when using POI in a sentence, always assume that the POI itself will insert a sentence fragment that begins with "the", "a/an", or is a proper noun.