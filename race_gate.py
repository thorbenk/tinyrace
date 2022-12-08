#!/usr/bin/env python

import cadquery as cq
import sys
import os

# size of electronic components
#
# neopixel stick
neopixel_width = 51
neopixel_height = 4
# on/off switch
on_off_switch_diameter = 12
# 16x2 LED display
lcd_cutout_width = 70.70
lcd_cutout_height = 23.80
# IR emitter / receiver LEDs
gate_led_diameter = 5

# size of materials
#
wood_thickness = 7
squared_timber_size = 20
wood_screw_diameter = 2
m4_screw_diameter = 4


cable_hole_diameter = 10
side_gate_dist = 2 * wood_thickness + squared_timber_size
gate_width = neopixel_width
gate_height = 40
gate_gate_width = 2 * wood_thickness + squared_timber_size
height = 90
depth = 110


lcd_offset_below = 15
lcd_offset_above = 15

neopixel_offset = 10

gate_led_side_dist = 10
gate_led_height = 12

cursor_buttons_x = 20
cursor_buttons_y = 15
cursor_button_diameter = 10

on_off_switch_height_offset = squared_timber_size + 20

screw_offset = 7.5

top_m4_screw_offset = 20

height = (
    gate_height
    + neopixel_offset
    + neopixel_height
    + lcd_offset_below
    + lcd_cutout_height
    + lcd_offset_above
)


def tag_box(box):
    box.faces("<X").tag("side_top")
    box.faces(">X").tag("side_right")
    box.faces("<Y").tag("side_bottom")
    box.faces(">Y").tag("side_top")
    box.faces("<X").edges("<Y").vertices(">Z").tag("front_bl")
    box.faces("<X").edges(">Y").vertices(">Z").tag("front_tl")
    box.faces(">X").edges("<Y").vertices(">Z").tag("front_br")
    box.faces(">X").edges(">Y").vertices(">Z").tag("front_tr")
    box.faces("<X").edges("<Y").vertices("<Z").tag("back_bl")
    box.faces("<X").edges(">Y").vertices("<Z").tag("back_tl")
    box.faces(">X").edges("<Y").vertices("<Z").tag("back_br")
    box.faces(">X").edges(">Y").vertices("<Z").tag("back_tr")


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


def make_front():

    w = 2 * (gate_gate_width / 2.0 + gate_width + side_gate_dist)
    h = height

    front = cq.Workplane("XY").polyline(pts).close().mirrorY().extrude(wood_thickness)
    front = (
        front.workplane()
        # drill hole between gates
        .moveTo(0, squared_timber_size / 2.0)
        .circle(wood_screw_diameter / 2.0)
        # LCD cutout
        .center(
            0,
            gate_height
            + neopixel_offset
            + neopixel_height
            + lcd_offset_below
            + lcd_cutout_height / 2.0,
        )
        .rect(lcd_cutout_width, lcd_cutout_height)
        .cutThruAll()
        # neopixel cutout (Gate A)
        .workplane(
            offset=0,
            origin=(
                gate_gate_width / 2.0 + gate_width / 2.0,
                gate_height + neopixel_offset + neopixel_height / 2.0,
            ),
        )
        .rect(neopixel_width, neopixel_height)
        .cutThruAll()
        # neopixel cutout (Gate B)
        .workplane(
            offset=0,
            origin=(
                -(gate_gate_width / 2.0 + gate_width / 2.0),
                gate_height + neopixel_offset + neopixel_height / 2.0,
            ),
        )
        .rect(neopixel_width, neopixel_height)
        # drill holes (left/right)
        .cutThruAll()
        .faces(">Z")
        .vertices("<XY")
        .workplane(centerOption="CenterOfMass")
        #   -> lower left vertex is center
        .center(wood_thickness + squared_timber_size / 2.0, squared_timber_size / 2.0)
        .rect(
            w - 2 * wood_thickness - squared_timber_size,
            h - wood_thickness - squared_timber_size,
            centered=False,
            forConstruction=True,
        )
        .vertices()
        .circle(wood_screw_diameter / 2.0)
        .cutThruAll()
    )
    tag_box(front)
    return front


def make_back():
    w = 2 * (gate_gate_width / 2.0 + gate_width + side_gate_dist)
    h = height

    back = (
        cq.Workplane("XY")
        .polyline(pts)
        .close()
        .mirrorY()
        .extrude(wood_thickness)
        # drill hole between gates
        .faces(">Z")
        .workplane()
        .moveTo(0, squared_timber_size / 2.0)
        .circle(wood_screw_diameter / 2.0)
        .cutThruAll()
        # drill holes (left/right)
        .faces(">Z")
        .vertices("<XY")
        .workplane(centerOption="CenterOfMass")
        #  -> lower left vertex is center
        .center(wood_thickness + squared_timber_size / 2.0, squared_timber_size / 2.0)
        .rect(
            w - 2 * wood_thickness - squared_timber_size,
            h - wood_thickness - squared_timber_size,
            centered=False,
            forConstruction=True,
        )
        .vertices()
        .circle(wood_screw_diameter / 2.0)
        .cutThruAll()
    )
    tag_box(back)
    return back


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
        .faces(">Z")
        .vertices("<XY")
        .workplane(centerOption="CenterOfMass")
        .moveTo(squared_timber_size/2.0, top_m4_screw_offset)
        .rect(w-squared_timber_size, h - 2*top_m4_screw_offset, centered=False, forConstruction=True)
        .vertices()
        .hole(m4_screw_diameter)
    )
    tag_box(top)
    return top


def make_right():
    w, h = depth - 2 * wood_thickness, height

    screw_hole_x_bottom = gate_led_diameter / 2.0 + screw_offset + wood_screw_diameter / 2.0
    screw_hole_x_top = w / 2.0
    screw_hole_y = squared_timber_size / 2.0

    right = (
        cq.Workplane("XY")
        .rect(w, h)
        .center(-w / 2, -h / 2)
        # screw holes bottom
        .moveTo(gate_led_side_dist + screw_hole_x_bottom, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x_bottom, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        # screw holes top
        .moveTo(screw_hole_x_top, h - wood_thickness - screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .extrude(wood_thickness)
    )
    tag_box(right)
    return right


def make_left():
    w, h = depth - 2 * wood_thickness, height

    screw_hole_x_bottom = gate_led_diameter / 2.0 + screw_offset + wood_screw_diameter / 2.0
    screw_hole_x_top = w / 2.0
    screw_hole_y = squared_timber_size / 2.0

    left = (
        cq.Workplane("XY")
        .rect(w, h)
        .center(-w / 2, -h / 2)
        # switch
        .moveTo(w / 2, height - on_off_switch_height_offset)
        .circle(on_off_switch_diameter / 2.0)
        # screw holes bottom
        .moveTo(gate_led_side_dist + screw_hole_x_bottom, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x_bottom, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        # screw holes top
        .moveTo(screw_hole_x_top, h - wood_thickness - screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        # done
        .extrude(wood_thickness)
    )
    tag_box(left)
    return left


def make_gate_side(side="l"):
    w, h = depth - 2 * wood_thickness, gate_height

    if side == "l":
        screw_hole_x = (
            gate_led_diameter / 2.0 + screw_offset + wood_screw_diameter / 2.0
        )
    else:
        screw_hole_x = gate_led_diameter / 2.0 + 2 * (
            screw_offset + wood_screw_diameter / 2.0
        )

    screw_hole_y = squared_timber_size / 2.0

    box = (
        cq.Workplane("XY")
        .rect(w, h)
        # LED holes
        .center(-w / 2.0, -h / 2.0)
        .moveTo(gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        .moveTo(w - gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        # wood screws
        .moveTo(gate_led_side_dist + screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .extrude(wood_thickness)
    )
    tag_box(box)
    return box


def make_squared_timber_top():
    d = depth - 2 * wood_thickness
    w = squared_timber_size

    box = cq.Workplane("XY").box(w, w, d)
    tag_box(box)
    return box


def make_squared_timber_bottom(pos):
    d = depth - 2 * wood_thickness
    w = squared_timber_size

    offset = 0
    if pos == "l":
        hole_depth = w / 2.0
    elif pos == "m":
        hole_depth = w
    else:
        hole_depth = w / 2.0
        offset = -w / 2.0

    box = (
        cq.Workplane("XY")
        .box(w, w, d)
        .faces(">X")
        .workplane(offset=offset)
        .center(-w / 2.0, -d / 2.0)
        .moveTo(gate_led_height, gate_led_side_dist)
        .hole(gate_led_diameter, depth=hole_depth)
        .moveTo(gate_led_height, d - gate_led_side_dist)
        .hole(gate_led_diameter, depth=hole_depth)
        .faces(">Y")
        .workplane(centerOption="CenterOfMass")
        .center(0, -d / 2.0)
        .moveTo(0, gate_led_side_dist)
        .hole(gate_led_diameter, depth=w / 2)
        .moveTo(0, d - gate_led_side_dist)
        .hole(gate_led_diameter, depth=w / 2)
    )
    tag_box(box)
    return box


def make_topfloor():
    w, h = (
        2 * (gate_gate_width / 2 + gate_width + side_gate_dist - wood_thickness),
        depth - 2 * wood_thickness,
    )

    gate_a_begin_x = -w / 2 + side_gate_dist - wood_thickness

    box2 = (
        cq.Workplane("XY")
        .center(gate_a_begin_x + gate_width / 2, 0)
        .box(gate_width, h, wood_thickness)
    )
    box = cq.Workplane("XY").box(w, h, wood_thickness).union(toUnion=box2, clean=False)

    box.vertices(cq.selectors.NearestToPointSelector((gate_a_begin_x, 0))).tag(
        "gate_a_l"
    )

    box = (
        box.faces(">Z")
        .workplane(centerOption="CenterOfMass")
        .center(-w / 2.0, -h / 2.0)
        # cable holes left
        .moveTo(squared_timber_size / 2.0, gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
        .moveTo(squared_timber_size / 2.0, h - gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
        # cable holes right
        .moveTo(w - squared_timber_size / 2.0, gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
        .moveTo(w - squared_timber_size / 2.0, h - gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
        # cable holes middle
        .moveTo(w / 2.0, gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
        .moveTo(w / 2.0, h - gate_led_side_dist)
        .hole(cable_hole_diameter / 2.0)
    )

    tag_box(box)
    return box


left = make_left()
right = make_right()
top = make_top()
front = make_front()
back = make_back()
gate_a_l = make_gate_side("r")
gate_a_r = make_gate_side("l")
gate_b_l = make_gate_side("r")
gate_b_r = make_gate_side("r")
squared_timber_l = make_squared_timber_bottom("l")
squared_timber_m = make_squared_timber_bottom("m")
squared_timber_r = make_squared_timber_bottom("r")
squared_timber_top_l = make_squared_timber_top()
squared_timber_top_r = make_squared_timber_top()
topfloor = make_topfloor()


def make_assembly():
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
        .add(squared_timber_l, name="squared_timber_l", color=cq.Color("red"))
        .add(squared_timber_m, name="squared_timber_m", color=cq.Color("red"))
        .add(squared_timber_r, name="squared_timber_r", color=cq.Color("red"))
        .add(squared_timber_top_l, name="squared_timber_top_l", color=cq.Color("red"))
        .add(squared_timber_top_r, name="squared_timber_top_r", color=cq.Color("red"))
        .add(topfloor, name="topfloor", color=cq.Color("red"))
    )

    (
        gate.constrain("front", "FixedRotation", (0, 0, 0))
        .constrain("top", "FixedRotation", (-90, 0, 0))
        .constrain("topfloor", "FixedRotation", (-90, 0, 0))
        .constrain("left", "FixedRotation", (0, 90, 0))
        .constrain("right", "FixedRotation", (0, 90, 0))
        .constrain("back", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_l", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_m", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_r", "FixedRotation", (0, 0, 0))
        .constrain("gate_a_l", "FixedRotation", (0, 90, 0))
        .constrain("squared_timber_top_l", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_top_r", "FixedRotation", (0, 0, 0))
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
        .constrain("left?back_bl", "front?back_bl", "Point")
        .constrain("right?front_bl", "front?back_br", "Point")
        .constrain("right?front_br", "back?front_br", "Point")
        .constrain("top?front_bl", "left?front_tl", "Point")
        .constrain("left?front_bl", "squared_timber_l?front_bl", "Point")
        .constrain("gate_a_r?front_bl", "squared_timber_m?front_bl", "Point")
        .constrain("gate_b_r?front_bl", "squared_timber_r?front_bl", "Point")
        .constrain("top?back_bl", "squared_timber_top_l?front_tl", "Point")
        .constrain("top?back_br", "squared_timber_top_r?front_tr", "Point")
        .constrain("topfloor?gate_a_l", "gate_a_l?front_tl", "Point")
        .solve()
    )

    return gate


if len(sys.argv) <= 1:
    gate = make_assembly()
    show_object(gate, name="gate")
else:
    print("height, depth:", height, depth)
    print(
        "Gate LED - LED distance:", depth - 2 * wood_thickness - 2 * gate_led_side_dist
    )

    export = {
        "front": front,
        "back": back,
        "left": left,
        "right": right,
        "top": top,
        "gate_a_l": gate_a_l,
        "gate_a_r": gate_a_r,
        "gate_b_l": gate_b_l,
        "gate_b_r": gate_b_r,
        "topfloor": topfloor,
    }
    for k, v in export.items():
        print(f"exporting {k}")
        cq.exporters.export(v, f"{k}.dxf")
        cmd = f"/usr/bin/python3 /usr/share/inkscape/extensions/dxf_input.py --scale=1.0 {k}.dxf > /tmp/a.svg"
        print("  - running ", cmd)
        os.system(cmd)

        cmd = f"inkscape --export-type=svg -o {k}.svg --export-area-drawing /tmp/a.svg"
        print("  - running ", cmd)
        os.system(cmd)

        cmd = f"inkscape --export-area-drawing --batch-process --export-type=pdf --export-filename={k}.pdf {k}.svg"
        print("  - running ", cmd)
        os.system(cmd)


# debug(top.faces(">Z").val())
# debug(front.faces("<Z").val())
# debug(left_topleft)
