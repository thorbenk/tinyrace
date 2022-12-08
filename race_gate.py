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


side_gate_dist = 2 * wood_thickness + squared_timber_size
gate_width = neopixel_width
gate_height = 40
gate_gate_width = 2 * wood_thickness + squared_timber_size
height = 90
depth = 110


lcd_offset_below = 15
lcd_offset_above = 15

neopixel_offset = 10

gate_led_side_dist = 7
gate_led_height = 12

cursor_buttons_x = 20
cursor_buttons_y = 15
cursor_button_diameter = 10

on_off_switch_height_offset = 30

screw_offset = 7.5

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
    front = cq.Workplane("XY").polyline(pts).close().mirrorY().extrude(wood_thickness)
    front = (
        front.workplane(offset=0)
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
    tag_box(front)
    return front


def make_back():
    back = cq.Workplane("XY").polyline(pts).close().mirrorY().extrude(wood_thickness)
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
    )
    tag_box(top)
    return top


def make_right():
    w, h = depth - 2 * wood_thickness, height

    screw_hole_x = gate_led_diameter / 2.0 + screw_offset + wood_screw_diameter / 2.0
    screw_hole_y = squared_timber_size / 2.0

    right = (
        cq.Workplane("XY")
        .rect(w, h)
        .center(-w / 2, -h / 2)
        .moveTo(gate_led_side_dist + screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .extrude(wood_thickness)
    )
    tag_box(right)
    return right


def make_left():
    w, h = depth - 2 * wood_thickness, height

    screw_hole_x = gate_led_diameter / 2.0 + screw_offset + wood_screw_diameter / 2.0
    screw_hole_y = squared_timber_size / 2.0

    left = (
        cq.Workplane("XY")
        .rect(w, h)
        .center(-w / 2, -h / 2)
        .moveTo(w / 2, height - on_off_switch_height_offset)
        .circle(on_off_switch_diameter / 2.0)
        .moveTo(gate_led_side_dist + screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
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
        .center(-w / 2.0, -h / 2.0)
        .moveTo(gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        .moveTo(w - gate_led_side_dist, gate_led_height)
        .circle(gate_led_diameter / 2.0)
        .moveTo(gate_led_side_dist + screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .moveTo(w - gate_led_side_dist - screw_hole_x, screw_hole_y)
        .circle(wood_screw_diameter / 2.0)
        .extrude(wood_thickness)
    )
    tag_box(box)
    return box


def make_squared_timber():
    d = depth - 2 * wood_thickness
    box = cq.Workplane("XY").rect(squared_timber_size, squared_timber_size).extrude(d)
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
squared_timber_l = make_squared_timber()
squared_timber_m = make_squared_timber()
squared_timber_r = make_squared_timber()


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
    )

    (
        gate.constrain("front", "FixedRotation", (0, 0, 0))
        .constrain("top", "FixedRotation", (-90, 0, 0))
        .constrain("left", "FixedRotation", (0, 90, 0))
        .constrain("right", "FixedRotation", (0, 90, 0))
        .constrain("back", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_l", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_m", "FixedRotation", (0, 0, 0))
        .constrain("squared_timber_r", "FixedRotation", (0, 0, 0))
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
        .constrain("left?back_bl", "front?back_bl", "Point")
        .constrain("right?front_bl", "front?back_br", "Point")
        .constrain("right?front_br", "back?front_br", "Point")
        .constrain("top?front_bl", "left?front_tl", "Point")
        .constrain("left?front_bl", "squared_timber_l?front_bl", "Point")
        .constrain("gate_a_r?front_bl", "squared_timber_m?front_bl", "Point")
        .constrain("gate_b_r?front_bl", "squared_timber_r?front_bl", "Point")
        .solve()
    )

    return gate


if len(sys.argv) <= 1:
    gate = make_assembly()
    print(gate)
    show_object(gate, name="gate")
else:
    print("height, depth:", height, depth)

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
