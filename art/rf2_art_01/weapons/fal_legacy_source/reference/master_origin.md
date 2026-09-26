# FAL master v01 — candidate, not production

Built-in imagegen, 2026-09-10. Original generated composition; no Mosin or
third-party game pixels used. Source and runtime copy are byte-identical.

Prompt: one classic FN FAL 50.00 first-person idle sprite on transparent RGBA,
view from shooter, butt lower right and straight barrel receding toward upper
centre-left; pale adult male hands with anatomically plausible contact, black
cotton hoodie sleeves and ribbed cuffs; matte steel/polymer, neutral upper-left
light; no optics, rails, text, HUD, muzzle flash, scenery or cast backdrop.

The returned master is 1536×1024 RGBA. Two later extraction attempts returned
RGB checkerboards and were rejected; they are not runtime assets. The original
alpha is retained unmodified and examined in engine, with the default sprite
alpha handling. A coherent rigid-pose recoil is authored in ZScript; this is
not a completed reload/bolt/empty animation family.

TEXTURES.txt controls logical size and position. Hands/receiver identity,
anatomy under motion and definitive perspective still need owner review.
M1 remains blocked on completing the family, enemy, room and audio.
