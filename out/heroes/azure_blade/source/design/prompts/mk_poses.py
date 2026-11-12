import pathlib

D = pathlib.Path(r"C:\Users\vinhtv13\Desktop\frt\fal-image-lab\out\heroes\azure_blade\source\design\prompts")
p2 = (D / "master_p02.txt").read_text(encoding="utf-8")
design = p2.split(" NEAR-FRONT VIEW")[0]
# design: the sword is described as held in one hand; poses change the grip, so cut the hand sentences
design = design.split(" In the hand on the LEFT side")[0]
sword = (" The weapon is ONE medium-length single-edged curved sword (a dao), the blade about as long as from his waist to his knee, "
         "pale steel with a thin amber edge line and an amber hilt wrap, long enough to read clearly but shorter than his legs.")
tail = p2[p2.index(" Background:"):]
no_extra = (" No buckles, no pouches, no rope, no bandages, no spikes, no stitches, no fabric texture: armour is a few big flat angular plates with sharp corners. "
            "At most three colour families. NO effects of any kind: no slash trail, no motion lines, no glow, no dust, no sparks, no impact ring, no shadow on the ground. "
            "The character, the sword and the cape stay inside the frame with margin on every side.")

pose_a = (
    " POSE A of a two-part attack, SIDE VIEW: his whole body is turned SIDEWAYS, a pure profile facing RIGHT (the face looking to the right, only one eye visible, "
    "the near shoulder toward the viewer). Both feet planted on ONE horizontal ground line, a medium-wide stance, knees only slightly bent, the torso leaning back a little to load the strike. "
    "BOTH ARMS are raised straight up above his head, the two forearms and the two fists of the SAME size, BOTH fists gripping the sword hilt together at the top, one fist right above the other, "
    "elbows bent and open. The sword is held in a reverse grip: the hilt is at the top between the fists and the BLADE POINTS STRAIGHT DOWN toward the ground, hanging just BEHIND his head and back "
    "(on the LEFT side of the image), the curved edge facing backward, the tip ending about at shoulder-blade height, clear of the head. "
    "The short cape hangs straight down BEHIND his back (on the LEFT side of the image), clearly behind the body. Both arms visible, neither hidden. "
    "Full body, centered, the whole figure including the raised fists and the sword inside the frame, filling about 75% of the frame height."
)
pose_b = (
    " POSE B of a two-part attack, SIDE VIEW, the moment of landing after a huge downward chop: a pure profile facing RIGHT. He is crouched LOW and bent forward: the front leg bent deeply at the knee "
    "with the thigh almost horizontal, the back leg stretched far behind him with the knee close to the ground and the toes planted, the torso bent forward and down, the head lowered, looking at the ground in front. "
    "BOTH ARMS reach forward and down, the two arms and the two fists of the SAME size, BOTH fists gripping the sword hilt together just above the ground in front of his front knee. "
    "The sword has just CHOPPED DOWN and is NOT stuck in the ground: the whole BLADE lies HORIZONTAL, perfectly PARALLEL to the ground, resting flat ON the ground line (its edge touching the ground), "
    "pointing FORWARD to the RIGHT of the image, the full length of the blade visible from the hilt to the tip, the curved edge facing down. "
    "The short cape is thrown UP and FORWARD by the motion and spreads over his bent back, so the cape and his back are clearly visible from the side. "
    "Everything stands on ONE horizontal ground line. Full body, centered, the whole figure including the stretched back leg, the cape and the full sword inside the frame with a clear margin of at least 8% on every side, so draw the figure a little smaller, filling about 65% of the frame width."
)
ref_a = ("The attached image is the approved master of this exact character: keep EXACTLY the same face, hair, headband, armour, colours, proportions, body size and sword design; "
         "only the pose changes. Draw the pose described below, not the standing pose of the attached image. ")
ref_b = ("The first attached image is the approved master of this exact character, the second attached image is the same character in the previous pose (pose A). "
         "Keep EXACTLY the same face, hair, headband, armour, colours, proportions, body size and sword design as in both images, the same size of the figure as in the second image; "
         "do NOT copy the pose of either image: draw only the new pose described below. ")
for name, pose, ref in (("pose_skill_crescent_p1", pose_a, ref_a), ("pose_skill_crescent_p2", pose_b, ref_b)):
    txt = ref + design + sword + pose + no_extra + tail
    (D / f"{name}_p01.txt").write_text(txt, encoding="utf-8")
    print(name, len(txt))
