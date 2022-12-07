import cadquery as cqk

# result = cq.Workplane().box(10, 10, 10)

side_gate_dist = 30
gate_width = 51
gate_height = 40
gate_gate_width = 30
height = 90
depth = 110

wood_thickness = 7

lcd_offset_below = 15
lcd_cutout_width = 70.70
lcd_cutout_height = 23.80
lcd_offset_above = 15

neopixel_offset = 10
neopixel_width = gate_width
neopixel_height = 4

gate_led_side_dist = 7
gate_led_height = 12
gate_led_diameter = 5

cursor_buttons_x = 20
cursor_buttons_y = 15
cursor_button_diameter = 10

height = gate_height + neopixel_offset + neopixel_height + lcd_offset_below + lcd_cutout_height + lcd_offset_above

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
    .center(0, gate_height + neopixel_offset +neopixel_height + lcd_offset_below + lcd_cutout_height / 2.0)
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


def make_top():
    w, h = (
        2 * (gate_gate_width / 2 + gate_width + side_gate_dist - wood_thickness),
        depth - 2 * wood_thickness,
    )
    top = (
        cq.Workplane("XY")
        .rect(w, h)
        .pushPoints(
            [
                (-cursor_buttons_x, 0),
                (cursor_buttons_x, 0),
                (0, -cursor_buttons_y),
                (0, cursor_buttons_y),
            ]
        )
        .circle(cursor_button_diameter / 2.0)
        .extrude(wood_thickness)
    )
    top.faces("<X").edges("<Y").vertices("<Z").tag("bl")
    top.faces("<X").edges(">Y").vertices("<Z").tag("tl")
    top.faces("<X").edges("<Y").vertices(">Z").tag("br")
    top.faces("<X").edges(">Y").vertices(">Z").tag("tr")
    return top


top = make_top()


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
    gate.constrain("top", "FixedRotation", (90, 0, 0))
    .constrain("left", "FixedRotation", (0, 0, 0))
    .constrain("right", "FixedRotation", (0, 0, 0))
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
    .constrain("left?tr", "top?tl", "Point")
    .constrain("back@faces@>Z", "left@faces@<Z", "Axis")
    .constrain("left?back_tl", "back?tl", "Point")
    .solve()
)

show_object(gate, name="gate")
# debug(top.faces(">Z").val())
# debug(front.faces("<Z").val())
# debug(left_topleft)
