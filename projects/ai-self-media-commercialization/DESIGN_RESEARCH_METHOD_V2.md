# Design Research & Method V2

Status: ACTIVE_PROJECT_METHOD
Scope: project-local only
Purpose: convert professional design principles into executable character-design gates before the next image-generation attempt.

## Why V1 failed

V1 over-invested in micro-signatures before solving macro-form appeal. It specified small facial asymmetries, hidden symbols, seam transitions and easter eggs while the face, body archetype, hair silhouette and garment silhouette were still generic.

V2 reverses the order: macro read first, micro detail last.

## 1. Character visual language — shape before detail

Research basis:
- Pixar visual-language teaching treats primitive shapes and silhouette as the foundation of character meaning; characters should remain identifiable by silhouette.
- Line, shape, space, tone, movement and color are compositional storytelling variables, not decorative labels.

Project rule:
Every design iteration must pass three black-silhouette tests before detail work:
1. head/hair/accessory silhouette;
2. nude/base body silhouette;
3. clothed silhouette.

If two different generic characters could share the same silhouette, the design is not locked.

## 2. Face design — primary masses before micro-asymmetry

V2 face-design order:
1. cranial width/height;
2. brow-plane shape;
3. eye-socket placement and spacing;
4. cheekbone/cheek-mass width;
5. nose volume and projection;
6. jaw angle and chin mass;
7. mouth width/position;
8. only then eyelid/brow/mouth micro-asymmetry.

Project rule:
The face must be recognizable in grayscale without blue hair, colored irises or pixel glasses.

Beauty optimization is not the target. Distinct proportion, readable planes and a coherent expression baseline are the target.

## 3. Body design — numbers are not a body archetype

Research basis:
- FIT figure drawing emphasizes line, gesture, composition, proportion and anatomy.
- Pixar shape-language examples show that a tall/thin figure only becomes characterful when the proportions and posture imply personality.

V2 body-design variables:
- head-to-body ratio;
- neck length and thickness;
- shoulder width/slope;
- ribcage width/depth;
- waist transition;
- pelvis width;
- arm-to-torso relation;
- thigh/calf balance;
- hand/foot scale;
- center of gravity;
- default line of action.

Project rule:
Design the base body before clothing. The character must already read as the intended adult observer in a plain fitted neutral outfit.

## 4. Fashion design — silhouette, proportion and balance before pockets

Research basis:
- Fashion Institute of Technology design fundamentals: shape/form, line, color and texture; principles include proportion/scale, balance, unity, rhythm and emphasis.
- FIT draping and apparel evaluation explicitly judge silhouette, balance, proportion, fabric behavior and whether detail is overdone or insufficient.

V2 costume order:
1. target body and use case;
2. garment silhouette;
3. garment-to-body proportion;
4. balance of visual mass;
5. dominant seam/opening lines;
6. fabric weight, stiffness and drape;
7. closure/pocket/function logic;
8. material hierarchy;
9. motif integration;
10. easter eggs.

Project rule:
No generic techwear detail is allowed unless it serves construction, function or the motif system.

A V2 garment must pass in a flat three-value blockout: light / dark / skin. Zippers, tabs, piping and micro-panels cannot rescue a weak silhouette.

## 5. Hair design — haircut architecture, not strand decoration

Research basis:
- Sassoon education treats line, graduation and layering as core methods for building shape; proportion, suitability and bone structure determine technique choice.

V2 hair order:
1. relationship to skull and face shape;
2. overall outer contour;
3. weight distribution;
4. line/graduation/layering logic;
5. primary masses;
6. secondary locks;
7. strand detail last.

Project rule:
The hair must pass a flat silhouette test and a side-profile test. Random spikes/flyaways are prohibited as identity substitutes.

## 6. Grooming / makeup — camera control, not idol beautification

Research basis:
- Professional male grooming for film/still photography aims for a natural, polished, camera-ready face; skin preparation, foundation/concealer, anti-shine, brows/eyes, contour and lips are used to enhance rather than visibly decorate.

Project rule:
Grooming supports facial planes and camera readability. It must not homogenize the character into K-idol / beauty-ad skin.

Keep:
- natural skin value and undertone;
- controlled shine;
- natural brow density;
- visible but subtle orbital depth;
- low-saturation lips.

## 7. Photography — identity reference must not distort design

Research basis:
- Nikon notes that facial shape is strongly affected by focal length and that 85mm is a classic portrait range for natural/flattering facial perspective.

Project rule:
Canon face/body validation uses neutral perspective and lighting. Dramatic lens choices are for storytelling later, not for deciding anatomy.

Identity-reference target:
- ~70–105mm equivalent for face/upper body;
- neutral eye-level camera;
- moderate depth of field;
- simple light;
- no fashion-editorial pose.

## 8. Directing / performance — pose must communicate role

Project rule:
Separate three pose classes:

A. DESIGN TRUTH
- neutral balanced stance;
- hands visible where possible;
- exposes shoulder/pelvis/limb relationships and garment balance;
- no lookbook attitude.

B. OBSERVER PERFORMANCE
- small head/eye shift toward evidence;
- restrained hand indication;
- body remains stable.

C. ABSURDITY RESPONSE
- environment/action changes more than the face;
- slight additional head tilt/pause;
- no exaggerated surprise.

Hands-in-pockets fashion posing is not accepted as a default canon pose.

## 9. Motif fusion — macro / meso / micro hierarchy

V2 requires exactly three levels:

### Macro contradiction
A design contradiction visible in silhouette or major massing. It must change the character's first or second read.

### Meso contradiction
A structural transition in hair, garment or accessory language that becomes visible at normal viewing distance.

### Micro easter eggs
Hidden symbols, codes, textile details or anomaly pixels for repeat viewers.

Project rule:
Do not add more micro easter eggs until macro and meso levels pass.

## 10. Prompt engineering for image models

The prompt is an execution spec, not a substitute for design.

Before writing a generation prompt, freeze these design outputs:
- face proportion diagram;
- base-body proportion diagram;
- hair silhouette front/side;
- garment silhouette front/side;
- 3-value color blockout;
- signature accessory scale and placement;
- macro/meso/micro motif map.

Then convert each into observable image instructions.

Do not ask the image model to invent all of these simultaneously from prose.

## V2 gate sequence

G0 — RESEARCH / DESIGN INTENT
G1 — FACE PRIMARY MASSES
G2 — BASE BODY ARCHETYPE
G3 — HAIR SILHOUETTE
G4 — COSTUME SILHOUETTE & PROPORTION
G5 — SIGNATURE ACCESSORY SCALE
G6 — MOTIF MACRO/MESO FUSION
G7 — COLOR & MATERIAL
G8 — GROOMING / MICRO DETAIL
G9 — EASTER EGGS
G10 — CANON PHOTOGRAPHY / TURNAROUND

No later gate can compensate for an earlier failed gate.

## Sources consulted

- Pixar in a Box / Khan Academy — Visual Language: shape, silhouette, line, composition, movement, tone and color.
  https://www.khanacademy.org/computing/pixar/storytelling/visual-language/v/video2
  https://www.khanacademy.org/computing/pixar/storytelling/visual-language/v/storytelling-line
- Fashion Institute of Technology — Elements and Principles of Fashion Design; draping/figure-drawing and fashion-design learning outcomes.
  https://www.fitnyc.edu/museum/documents/elements-and-principles-of-fashion-design.pdf
  https://catalog.fitnyc.edu/undergraduate/courses/dp/
  https://catalog.fitnyc.edu/undergraduate/courses/fa/
  https://www.fitnyc.edu/academics/academic-divisions/art-and-design/fashion-design/degree-details/outcomes.php
- Sassoon Academy — ABC / ABC Men: line, graduation, layering, proportion, suitability and bone structure.
  https://www.sassoon-academy.com/media/rfeh10w3/sassoon_us-courses-overview-2024.pdf
- Kryolan Professional Make-up — Male Grooming: natural camera-ready enhancement and anti-shine / brow / contour / lip control.
  https://mu-fr.kryolan.com/manifestation/focus-male-grooming
- Nikon — portrait focal length and facial perspective; 85mm as a classic portrait range.
  https://www.nikonusa.com/p/nikkor-z-85mm-f18-s/20090/overview
