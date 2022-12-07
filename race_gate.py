import cadquery as cq

# result = cq.Workplane().box(10, 10, 10)

side_gate_dist = 3
gate_width = 5
gate_height = 4
lcd_offset = 2
gate_gate_width = 2
height = 8
depth = 11

wood_thickness = 0.7

lcd_cutout_width = 4
lcd_cutout_height = 1

neopixel_offset = 1
neopixel_width = gate_width
neopixel_height = 0.4

gate_led_side_dist = 0.7
gate_led_height = 1.2
gate_led_diameter = 0.5

pts = [
    (0, 0),
    (gate_gate_width / 2.0, 0),
    (gate_gate_width / 2.0, gate_height),
    (gate_gate_width / 2.0 + gate_width, gate_height),
    (gate_gate_width / 2.0 + gate_width, 0),
    (gate_gate_width / 2.0 + gate_width + side_gate_dist, 0),
    (gate_gate_width / 2.0 + gate_width + side_gate_dist, height),
    (0, height),
]

front = cq.Workplane("XY").polyline(pts).close().mirrorY().extrude(wood_thickness)

back = cq.Workplane("XY").polyline(pts).close().mirrorY().extrude(wood_thickness)

front = (
    front.workplane(offset=0)
    .center(0, gate_height + lcd_offset + lcd_cutout_height / 2.0)
    .rect(lcd_cutout_width, lcd_cutout_height)
    .cutThruAll()
    .workplane(
        offset=0,
        origin=(
            gate_gate_width / 2.0 + gate_width / 2.0,
            gate_height + neopixel_offset + neopixel_height / 2.0,
        ),
    )
    .rect(neopixel_width, neopixel_height)
    .cutThruAll()
    .workplane(
        offset=0,
        origin=(
            -(gate_gate_width / 2.0 + gate_width / 2.0),
            gate_height + neopixel_offset + neopixel_height / 2.0,
        ),
    )
    .rect(neopixel_width, neopixel_height)
    .cutThruAll()
)

# front.faces(">Z").tag("Z").end()

top = (
    cq.Workplane("XZ")
    .rect(
        2 * (gate_gate_width / 2 + gate_width + side_gate_dist - wood_thickness),
        depth - 2 * wood_thickness,
    )
    .extrude(wood_thickness)
)


left = (
    cq.Workplane("YZ").rect(height, depth - 2 * wood_thickness).extrude(wood_thickness)
)

right = (
    cq.Workplane("YZ").rect(height, depth - 2 * wood_thickness).extrude(wood_thickness)
)


def make_gate_side():
    w, h = depth - 2 * wood_thickness, gate_height
    return (
        cq.Workplane("XY")
        .rect(w, h)
        .center(-w / 2.0, -h / 2.0)
        .moveTo(gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        .moveTo(w - gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        .extrude(wood_thickness)
    )


front.faces("<Z").edges("<X").vertices("<Y").tag("bl")
front.faces("<Z").edges("<X").vertices(">Y").tag("tl")
front.faces("<Z").edges(">X").vertices("<Y").tag("br")
front.faces("<Z").edges(">X").vertices(">Y").tag("tr")

back.faces(">Z").edges("<X").vertices("<Y").tag("bl")
back.faces(">Z").edges("<X").vertices(">Y").tag("tl")
back.faces(">Z").edges(">X").vertices("<Y").tag("br")
back.faces(">Z").edges(">X").vertices(">Y").tag("tr")

top.faces(">Z").edges("<X").vertices("<Y").tag("bl")
top.faces(">Z").edges("<X").vertices(">Y").tag("tl")
top.faces(">Z").edges(">X").vertices("<Y").tag("br")
top.faces(">Z").edges(">X").vertices(">Y").tag("tr")

left.faces(">Z").edges("<X").vertices("<Y").tag("bl")
left.faces(">Z").edges("<X").vertices(">Y").tag("tl")
left.faces(">Z").edges(">X").vertices("<Y").tag("br")
left.faces(">Z").edges(">X").vertices(">Y").tag("tr")

left.faces("<Z").edges("<X").vertices(">Y").tag("back_tl")

right.faces(">Z").edges(">X").vertices("<Y").tag("br")
right.faces(">Z").edges(">X").vertices(">Y").tag("tr")
right.faces(">Z").edges("<X").vertices("<Y").tag("bl")
right.faces(">Z").edges("<X").vertices(">Y").tag("tl")

gate_a_l = make_gate_side()
gate_a_r = make_gate_side()
gate_b_l = make_gate_side()
gate_b_r = make_gate_side()


gate = (
    cq.Assembly()
    .add(front, name="front", color=cq.Color("yellow"))
    .add(top, name="top", color=cq.Color("black"))
    .add(left, name="left", color=cq.Color("blue"))
    .add(right, name="right", color=cq.Color("orange"))
    .add(back, name="back", color=cq.Color("gray"))
    .add(gate_a_l, name="gate_a_l", color=cq.Color("red"))
    .add(gate_a_r, name="gate_a_r", color=cq.Color("orange"))
    .add(gate_b_l, name="gate_b_l", color=cq.Color("blue"))
    .add(gate_b_r, name="gate_b_r", color=cq.Color("yellow"))
)

(
    gate.constrain("top", "FixedRotation", (0, 0, 0))
    .constrain("left", "FixedRotation", (0, 0, 0))
    .constrain("right", "FixedRotation", (0, 0, 0))
    .constrain("top", "FixedRotation", (0, 0, 0))
    .constrain("back", "FixedRotation", (0, 0, 0))
    .constrain("gate_a_l", "FixedRotation", (0, 90, 0))
    .constrain(
        "gate_a_l",
        gate_a_l.faces(">Z").edges("<X").vertices("<Y").val(),
        "front",
        front.vertices(
            cq.selectors.NearestToPointSelector(
                (-(gate_gate_width / 2.0 + gate_width), 0, 0)
            )
        ).val(),
        "Point",
    )
    .constrain("gate_a_r", "FixedRotation", (0, 90, 0))
    .constrain(
        "gate_a_r",
        gate_a_r.faces("<Z").edges("<X").vertices("<Y").val(),
        "front",
        front.vertices(
            cq.selectors.NearestToPointSelector((-gate_gate_width / 2.0, 0, 0))
        ).val(),
        "Point",
    )
    .constrain("gate_b_l", "FixedRotation", (0, 90, 0))
    .constrain(
        "gate_b_l",
        gate_b_l.faces(">Z").edges("<X").vertices("<Y").val(),
        "front",
        front.vertices(
            cq.selectors.NearestToPointSelector((gate_gate_width / 2.0, 0, 0))
        ).val(),
        "Point",
    )
    .constrain("gate_b_r", "FixedRotation", (0, 90, 0))
    .constrain(
        "gate_b_r",
        gate_b_r.faces("<Z").edges("<X").vertices("<Y").val(),
        "front",
        front.vertices(
            cq.selectors.NearestToPointSelector(
                (gate_gate_width / 2.0 + gate_width, 0, 0)
            )
        ).val(),
        "Point",
    )
    .constrain("front@faces@<Z", "left@faces@>Z", "Axis")
    .constrain("left?bl", "front?bl", "Point")
    .constrain("front@faces@<Z", "right@faces@>Z", "Axis")
    .constrain("right?br", "front?br", "Point")
    .constrain("front@faces@<Z", "top@faces@>Z", "Axis")
    .constrain("left?tr", "top?tl", "Point")
    .constrain("back@faces@>Z", "left@faces@<Z", "Axis")
    .constrain("left?back_tl", "back?tl", "Point")
    .solve()
)

show_object(gate, name="gate")
# debug(top.faces(">Z").val())
# debug(front.faces("<Z").val())
# debug(left_topleft)
