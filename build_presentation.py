"""
Build 16-slide Minor Project presentation by editing the existing university PPT.

The script:
  1. Opens the original PPT to preserve theme, slide master, backgrounds.
  2. Extracts reusable assets (logo image bytes).
  3. Deletes every existing slide.
  4. Adds 16 new slides using the same layouts.
  5. Rebuilds template elements (logo, slide-number box) identically.
  6. Populates each slide with the new project content.

Run:  python build_presentation.py
"""

import copy, io, os
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.chart.data import CategoryChartData
from lxml import etree

# ═══════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════
SRC_PPT  = Path(r"D:\Downloads\minor project.pptx")
OUT_PPT  = Path(r"C:\Users\victus\Desktop\Ai-Based-Career-Recommendation-System"
                r"\AI_Based_Resume_Analyzer_Project_Presentation.pptx")
LOGO_DIR = Path(r"C:\Users\victus\Desktop\Ai-Based-Career-Recommendation-System\_ppt_images")

# ═══════════════════════════════════════════════════
# TEMPLATE CONSTANTS (measured from original PPT)
# ═══════════════════════════════════════════════════
# Slide-number box (orange #DD8047, white text, TNR 12 pt bold)
NUM_LEFT, NUM_TOP = 0, 1280160
NUM_W, NUM_H = 533400, 228600
NUM_FILL = "DD8047"

# Logo position on content slides
LOGO_LEFT, LOGO_TOP = 8229600, 228600
LOGO_W, LOGO_H = 743184, 885264

# Title placeholder typical position (content slides)
TITLE_LEFT, TITLE_TOP = 2438400, 228600
TITLE_W, TITLE_H = 4167188, 695325

# Content area
CONTENT_LEFT = 533400
CONTENT_TOP  = 1676400
CONTENT_W    = 8229600

# Fonts and colours from original
FONT = "Times New Roman"
FONT_SANS = "Calibri"
BLUE       = RGBColor(0x2E, 0x74, 0xB5)
DARK_BLUE  = RGBColor(0x1F, 0x4E, 0x79)
HEADING_BLUE = RGBColor(0x00, 0x70, 0xC0)
WHITE      = RGBColor(0xFF, 0xFF, 0xFF)
BLACK      = RGBColor(0x00, 0x00, 0x00)
GRAY       = RGBColor(0x59, 0x56, 0x59)
LIGHT_GRAY = RGBColor(0xF2, 0xF2, 0xF2)
GREEN      = RGBColor(0x00, 0x70, 0x30)
AMBER      = RGBColor(0xED, 0x7D, 0x31)
RED_STATUS = RGBColor(0xC0, 0x00, 0x00)
LIGHT_BLUE = RGBColor(0xD6, 0xE4, 0xF0)
LIGHT_GREEN= RGBColor(0xE2, 0xEF, 0xDA)
LIGHT_ORANGE=RGBColor(0xFC, 0xE4, 0xD6)
PURPLE_LIGHT=RGBColor(0xD5, 0xC3, 0xE8)

# ═══════════════════════════════════════════════════
# 1.  OPEN ORIGINAL & EXTRACT ASSETS
# ═══════════════════════════════════════════════════
prs = Presentation(str(SRC_PPT))

# Extract the small logo (71 kB, appears on content slides 2-14)
small_logo_bytes = None
for shape in prs.slides[1].shapes:        # Slide 2
    if shape.shape_type == 13:            # PICTURE
        small_logo_bytes = shape.image.blob
        small_logo_ext  = shape.image.content_type.split("/")[-1]
        break

# Extract the large logo (138 kB, on Thank You slide)
large_logo_bytes = None
for shape in prs.slides[14].shapes:       # Slide 15 (Thank You)
    if shape.shape_type == 13:
        large_logo_bytes = shape.image.blob
        large_logo_ext   = shape.image.content_type.split("/")[-1]
        break

# Also extract the smaller logo used on slide 1 (in the middle)
slide1_logo_bytes = None
for shape in prs.slides[0].shapes:
    if shape.shape_type == 13:
        slide1_logo_bytes = shape.image.blob
        slide1_logo_ext   = shape.image.content_type.split("/")[-1]
        break

# ═══════════════════════════════════════════════════
# 2.  DELETE ALL EXISTING SLIDES
# ═══════════════════════════════════════════════════
while len(prs.slides) > 0:
    rId = prs.slides._sldIdLst[0].get(
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    )
    prs.part.drop_rel(rId)
    sldId = prs.slides._sldIdLst[0]
    prs.slides._sldIdLst.remove(sldId)

print(f"Slides after deletion: {len(prs.slides)}")

# ═══════════════════════════════════════════════════
# LAYOUT REFERENCES
# ═══════════════════════════════════════════════════
layout_map = {sl.name: sl for sl in prs.slide_layouts}
blank_layout   = layout_map.get("Blank", prs.slide_layouts[4])
title_layout   = layout_map.get("Title and Content", prs.slide_layouts[1])
title_only_layout = layout_map.get("Title Only", prs.slide_layouts[3])

# ═══════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════

def _save_temp(blob, ext):
    """Write blob to a temp file and return path."""
    p = LOGO_DIR / f"_tmp_logo.{ext}"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(blob)
    return str(p)

SMALL_LOGO_PATH = _save_temp(small_logo_bytes, small_logo_ext) if small_logo_bytes else None
LARGE_LOGO_PATH = _save_temp(large_logo_bytes, large_logo_ext) if large_logo_bytes else None
SLIDE1_LOGO_PATH = None
if slide1_logo_bytes:
    p = LOGO_DIR / f"_tmp_s1logo.{slide1_logo_ext}"
    p.write_bytes(slide1_logo_bytes)
    SLIDE1_LOGO_PATH = str(p)

def add_logo(slide):
    """Add the small university logo at the standard position."""
    if SMALL_LOGO_PATH:
        slide.shapes.add_picture(SMALL_LOGO_PATH,
                                 LOGO_LEFT, LOGO_TOP, LOGO_W, LOGO_H)

def add_slide_number(slide, number):
    """Replicate the orange slide-number box from the original template."""
    txBox = slide.shapes.add_textbox(Emu(NUM_LEFT), Emu(NUM_TOP),
                                     Emu(NUM_W), Emu(NUM_H))
    # Set background fill to match original (#DD8047)
    sp = txBox._element
    spPr = sp.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}spPr")
    if spPr is None:
        spPr = etree.SubElement(sp,
            "{http://schemas.openxmlformats.org/drawingml/2006/main}spPr")
    sf = etree.SubElement(spPr,
        "{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill")
    clr = etree.SubElement(sf,
        "{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
    clr.set("val", NUM_FILL)

    tf = txBox.text_frame
    tf.word_wrap = False
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = str(number)
    run.font.name = FONT
    run.font.size = Pt(12)
    run.font.bold = True
    run.font.color.rgb = WHITE


def add_title_text(slide, text, left=None, top=None, width=None, height=None,
                   font_size=Pt(24), center=True):
    """Add a title text box matching the original template style."""
    l = Emu(left) if left else Emu(TITLE_LEFT)
    t = Emu(top) if top else Emu(TITLE_TOP)
    w = Emu(width) if width else Emu(TITLE_W)
    h = Emu(height) if height else Emu(TITLE_H)
    txBox = slide.shapes.add_textbox(l, t, w, h)
    tf = txBox.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER if center else PP_ALIGN.LEFT
    run = p.add_run()
    run.text = text
    run.font.name = FONT
    run.font.size = font_size
    run.font.bold = True
    # Let the theme default apply (do not set explicit colour)
    return txBox


def add_textbox(slide, left, top, width, height, text, font_size=Pt(14),
                bold=False, color=BLACK, alignment=PP_ALIGN.LEFT,
                font_name=FONT, word_wrap=True):
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = word_wrap
    p = tf.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color
    return txBox


def add_bullet_list(slide, left, top, width, height, items,
                    font_size=Pt(14), color=BLACK, font_name=FONT,
                    bullet_char="\u2022", spacing_pt=3):
    """Add a text box with bullet points."""
    txBox = slide.shapes.add_textbox(Emu(left), Emu(top), Emu(width), Emu(height))
    tf = txBox.text_frame
    tf.word_wrap = True
    for i, item in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = PP_ALIGN.LEFT
        p.space_after = Pt(spacing_pt)
        p.space_before = Pt(1)
        run = p.add_run()
        run.text = f"{bullet_char}  {item}"
        run.font.name = font_name
        run.font.size = font_size
        run.font.color.rgb = color
    return txBox


def add_section_heading(slide, left, top, width, text, font_size=Pt(16)):
    """Add a coloured sub-heading (matches original #0070C0 style)."""
    return add_textbox(slide, left, top, width, Inches(0.35).emu, text,
                       font_size=font_size, bold=True, color=HEADING_BLUE)


def add_flowchart_box(slide, left, top, width, height, text,
                      fill_color=LIGHT_BLUE, text_color=BLACK,
                      font_size=Pt(9), border_color=BLUE):
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Emu(left), Emu(top), Emu(width), Emu(height))
    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color
    shape.line.color.rgb = border_color
    shape.line.width = Pt(1)
    tf = shape.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = text
    run.font.name = FONT_SANS
    run.font.size = font_size
    run.font.color.rgb = text_color
    return shape


def add_down_arrow(slide, cx, top, length=Inches(0.2).emu):
    arrow = slide.shapes.add_shape(MSO_SHAPE.DOWN_ARROW,
        Emu(cx - Inches(0.08).emu), Emu(top), Emu(Inches(0.16).emu), Emu(length))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = DARK_BLUE
    arrow.line.fill.background()
    return arrow


def add_right_arrow_shape(slide, left, cy, length=Inches(0.25).emu):
    arrow = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
        Emu(left), Emu(cy - Inches(0.05).emu), Emu(length), Emu(Inches(0.1).emu))
    arrow.fill.solid()
    arrow.fill.fore_color.rgb = DARK_BLUE
    arrow.line.fill.background()
    return arrow


def set_cell(cell, text, font_size=Pt(10), bold=False, color=BLACK,
             alignment=PP_ALIGN.LEFT, font_name=FONT):
    cell.text = ""
    p = cell.text_frame.paragraphs[0]
    p.alignment = alignment
    run = p.add_run()
    run.text = text
    run.font.name = font_name
    run.font.size = font_size
    run.font.bold = bold
    run.font.color.rgb = color


def set_cell_fill(cell, rgb):
    cell.fill.solid()
    cell.fill.fore_color.rgb = rgb


def _in(v):
    """Shorthand: inches to EMU integer."""
    return Inches(v).emu


def build_content_slide(title_text, slide_num):
    """Create a blank content slide with standard template elements."""
    slide = prs.slides.add_slide(blank_layout)
    add_title_text(slide, title_text)
    add_slide_number(slide, slide_num)
    add_logo(slide)
    return slide


# ═══════════════════════════════════════════════════
# ═══  SLIDE 1:  TITLE PAGE  ══════════════════════
# ═══════════════════════════════════════════════════
s1 = prs.slides.add_slide(title_layout)

# Title
add_textbox(s1, _in(1.1), _in(0.35), _in(7.1), _in(1.2),
            "AI-BASED RESUME ANALYZER AND\nCAREER RECOMMENDATION SYSTEM",
            font_size=Pt(30), bold=True, color=BLACK,
            alignment=PP_ALIGN.CENTER)

# Subtitle line
add_textbox(s1, _in(1.0), _in(1.7), _in(7.5), _in(0.4),
            "Current Implementation: Educational Data-Based STEM Prediction "
            "and Questionnaire-Based Career Recommendation",
            font_size=Pt(10), bold=False, color=GRAY,
            alignment=PP_ALIGN.CENTER, font_name=FONT)

# Team members
add_textbox(s1, _in(2.5), _in(2.35), _in(4.5), _in(1.1),
            "by:\n"
            "Rohit Prajapati (241B211)\n"
            "Sai Arpit (241B219)\n"
            "Samyak Jain (241B222)",
            font_size=Pt(14), bold=False, color=BLACK,
            alignment=PP_ALIGN.CENTER)

# Supervisor
add_textbox(s1, _in(2.5), _in(3.55), _in(4.5), _in(0.8),
            "Under the supervision of:\nDR. PRATEEK PANDEY",
            font_size=Pt(14), bold=True, color=BLACK,
            alignment=PP_ALIGN.CENTER)

# University logo (center)
if SLIDE1_LOGO_PATH:
    s1.shapes.add_picture(SLIDE1_LOGO_PATH,
                          Emu(4114800), Emu(4343400), Emu(1041399), Emu(1240490))

# University name
add_textbox(s1, _in(2.0), _in(6.5), _in(6.0), _in(0.4),
            "Jaypee University of Engineering & Technology, Guna",
            font_size=Pt(16), bold=False, color=BLACK,
            alignment=PP_ALIGN.CENTER)

# B.Tech semester info
add_textbox(s1, _in(2.0), _in(5.8), _in(6.0), _in(0.3),
            "B.Tech V Sem (A.Y. 2026-2027)  |  Minor Project Part-I",
            font_size=Pt(11), bold=False, color=GRAY,
            alignment=PP_ALIGN.CENTER)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 2:  INTRODUCTION  ════════════════════
# ═══════════════════════════════════════════════════
s2 = build_content_slide("1. INTRODUCTION", 2)

add_section_heading(s2, CONTENT_LEFT, _in(1.5), _in(4.0), "Brief Overview")

add_bullet_list(s2, CONTENT_LEFT, _in(1.9), _in(4.2), _in(2.2), [
    "Career guidance system for students in Classes 9-12",
    "Uses verified longitudinal educational data (HSLS:09)",
    "ML-based STEM career-fit estimation using CatBoost",
    "Questionnaire-based career exploration with 30 questions",
    "Provides career recommendations, skills and learning roadmaps",
], font_size=Pt(11))

add_section_heading(s2, CONTENT_LEFT, _in(4.1), _in(4.0), "Objectives")

add_bullet_list(s2, CONTENT_LEFT, _in(4.5), _in(4.2), _in(2.0), [
    "Analyse educational and career-related student data",
    "Develop a ML model for STEM career-fit estimation",
    "Profile student interests through structured questions",
    "Generate career suggestions with learning guidance",
], font_size=Pt(11))

# System overview diagram (right side)
add_section_heading(s2, _in(5.3), _in(1.5), _in(4.0), "System Overview", font_size=Pt(14))

box_y = _in(1.95)
add_flowchart_box(s2, _in(5.3), box_y, _in(3.8), _in(0.55),
    "Component A: ML-Based STEM Prediction\n(HSLS:09 Dataset + CatBoost)",
    fill_color=LIGHT_BLUE, font_size=Pt(9))
add_down_arrow(s2, _in(7.2), box_y + _in(0.57))
box_y += _in(0.85)

add_flowchart_box(s2, _in(5.3), box_y, _in(3.8), _in(0.55),
    "Component B: Questionnaire Recommendation\n(30 Questions + Scoring Algorithm)",
    fill_color=LIGHT_BLUE, font_size=Pt(9))
add_down_arrow(s2, _in(7.2), box_y + _in(0.57))
box_y += _in(0.85)

add_flowchart_box(s2, _in(5.3), box_y, _in(3.8), _in(0.45),
    "Flask Backend API\n(Model Serving + Recommendation Engine)",
    fill_color=LIGHT_GREEN, font_size=Pt(9))
add_down_arrow(s2, _in(7.2), box_y + _in(0.47))
box_y += _in(0.75)

add_flowchart_box(s2, _in(5.3), box_y, _in(3.8), _in(0.55),
    "Output: Career Recommendations\nExplanations + Skills + Roadmaps",
    fill_color=LIGHT_ORANGE, font_size=Pt(9))

add_textbox(s2, _in(5.3), _in(5.3), _in(4.0), _in(0.6),
    "Note: Current input mechanism is questionnaire-based\nstudent profiling. Resume parsing is a future extension.",
    font_size=Pt(9), color=GRAY, font_name=FONT_SANS)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 3:  PROBLEM STATEMENT  ═══════════════
# ═══════════════════════════════════════════════════
s3 = build_content_slide("2. PROBLEM STATEMENT", 3)

add_section_heading(s3, CONTENT_LEFT, _in(1.5), _in(4.2), "Problem Definition")

add_bullet_list(s3, CONTENT_LEFT, _in(1.9), _in(4.3), _in(2.5), [
    "Students lack structured, personalised career guidance",
    "Career decisions often based on incomplete information",
    "Generic recommendations do not explain suitability",
    "No guidance on relevant skills or practical learning steps",
    "Classes 9-12 students face critical stream/career choices\n  with limited data-driven support",
], font_size=Pt(11))

add_section_heading(s3, CONTENT_LEFT, _in(4.4), _in(4.2), "Why This Problem Matters")

add_bullet_list(s3, CONTENT_LEFT, _in(4.8), _in(4.3), _in(1.5), [
    "Early career decisions shape entire academic trajectory",
    "Uninformed choices lead to course and career mismatches",
    "Structured, evidence-based guidance is largely absent",
], font_size=Pt(11))

# Right side: problem-to-solution visual
add_section_heading(s3, _in(5.5), _in(1.5), _in(3.8), "Problem to Solution", font_size=Pt(14))

prob_items = ["No data-driven guidance", "No skill-level advice", "No personalised explanation"]
sol_items  = ["HSLS:09-based ML model", "Questionnaire profiling", "Explanations + roadmaps"]
py = _in(2.0)
for pr, sl in zip(prob_items, sol_items):
    add_flowchart_box(s3, _in(5.3), py, _in(1.65), _in(0.38),
                      pr, fill_color=LIGHT_ORANGE, font_size=Pt(8))
    add_right_arrow_shape(s3, _in(7.05), py + _in(0.17))
    add_flowchart_box(s3, _in(7.5), py, _in(1.65), _in(0.38),
                      sl, fill_color=LIGHT_GREEN, font_size=Pt(8))
    py += _in(0.5)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 4:  LITERATURE REVIEW (1/2)  ═════════
# ═══════════════════════════════════════════════════
s4 = build_content_slide("3. LITERATURE REVIEW (1/2)", 4)

add_section_heading(s4, CONTENT_LEFT, _in(1.45), _in(8.5),
                    "Summary of Existing Work")

sections = [
    ("Howard Gardner's Multiple Intelligences Theory",
     "Gardner (1983) proposed multiple distinct intelligences: linguistic, logical-mathematical, "
     "spatial, musical, bodily-kinaesthetic, interpersonal, intrapersonal and naturalistic. "
     "Our questionnaire sections map to these intelligence dimensions for career exploration."),

    ("Educational Data Mining (EDM)",
     "EDM applies data mining, ML and statistical methods to educational datasets for student "
     "performance prediction, dropout analysis and career path modelling. HSLS:09 is a widely "
     "used longitudinal dataset in EDM research (Baker & Yacef, 2009; Romero & Ventura, 2020)."),

    ("ML-Based Career Guidance Systems",
     "Prior work uses academic scores, aptitude tests or interest surveys for career prediction. "
     "CatBoost (Prokhorenkova et al., 2018) handles missing values natively and outperforms "
     "many gradient boosting methods on heterogeneous tabular data."),

    ("Skill-to-Job Matching and Recommendation Systems",
     "Systems like C3-IoC (Jose-Garcia et al., 2022) use ML and text mining to match student "
     "skills to job roles. Most existing systems lack personalised explanations or actionable "
     "learning guidance. Few combine longitudinal data with interest-based profiling."),
]

y = _in(2.05)
for heading, body in sections:
    add_textbox(s4, CONTENT_LEFT, y, _in(8.5), _in(0.25),
                heading, font_size=Pt(12), bold=True, color=HEADING_BLUE)
    y += _in(0.3)
    add_textbox(s4, CONTENT_LEFT, y, _in(8.5), _in(0.8),
                body, font_size=Pt(10), color=BLACK)
    y += _in(0.85)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 5:  LITERATURE REVIEW (2/2)  ═════════
# ═══════════════════════════════════════════════════
s5 = build_content_slide("3. LITERATURE REVIEW (2/2)", 5)

add_section_heading(s5, CONTENT_LEFT, _in(1.45), _in(8.5),
                    "Limitations, Gaps and Our Contribution")

# Comparison table
tbl_data = [
    ["Challenge", "Existing Limitation", "Our Approach"],
    ["Self-reported data",
     "Student responses may not reflect\nactual abilities",
     "Use validated HSLS:09 data with\nobjective test scores"],
    ["Dataset reliability",
     "Synthetic or small local datasets\nlack generalisability",
     "Selected HSLS:09: authentic,\nlongitudinal, government-sourced"],
    ["Class imbalance",
     "STEM aspirants are a minority;\nstandard accuracy misleading",
     "Class weighting; evaluation with\nROC-AUC and PR-AUC"],
    ["Explainability",
     "Black-box models do not explain\nwhy a career is recommended",
     "Match explanations, score\ncomponents and evidence provided"],
    ["Actionability",
     "Most systems stop at prediction\nwithout learning guidance",
     "Skills, beginner projects and\n4-week learning roadmaps"],
]

rows, cols = len(tbl_data), 3
tbl = s5.shapes.add_table(rows, cols, Emu(CONTENT_LEFT), Emu(_in(2.0)),
                          Emu(_in(8.5)), Emu(_in(3.2))).table
tbl.columns[0].width = Emu(_in(1.9))
tbl.columns[1].width = Emu(_in(3.3))
tbl.columns[2].width = Emu(_in(3.3))
for r in range(rows):
    for c in range(cols):
        cell = tbl.cell(r, c)
        if r == 0:
            set_cell(cell, tbl_data[r][c], Pt(10), True, WHITE, PP_ALIGN.CENTER)
            set_cell_fill(cell, DARK_BLUE)
        else:
            set_cell(cell, tbl_data[r][c], Pt(9), (c == 0), BLACK)
            if r % 2 == 0:
                set_cell_fill(cell, LIGHT_GRAY)

add_section_heading(s5, CONTENT_LEFT, _in(5.4), _in(8.5), "Research Gap Addressed")
add_textbox(s5, CONTENT_LEFT, _in(5.75), _in(8.5), _in(0.8),
    "Few systems combine longitudinal educational data analysis with structured interest "
    "profiling and provide actionable career exploration output. Our project integrates "
    "ML-based STEM estimation with questionnaire-based career recommendations, "
    "explanations, skills and learning roadmaps.",
    font_size=Pt(11), color=BLACK)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 6:  WORK PLAN (Weeks 1-13)  ══════════
# ═══════════════════════════════════════════════════
s6 = build_content_slide("4. WORK PLAN", 6)

add_section_heading(s6, CONTENT_LEFT, _in(1.4), _in(8.5),
                    "Weekly Progress Timeline (Weeks 1-13)")

add_textbox(s6, CONTENT_LEFT, _in(1.75), _in(8.5), _in(0.2),
    "Note: Weekly reports for Weeks 1-5 were not available for inspection. "
    "Activities for Weeks 1-5 are inferred from context. Weeks 6-10 are verified from submitted reports.",
    font_size=Pt(7), color=GRAY, font_name=FONT_SANS)

# Build weekly milestone cards as a compact vertical timeline
# Each week gets its own row
weeks = [
    ("Week 1",  "Jul 2026",              "Topic selection and initial project discussion",        "Completed"),
    ("Week 2",  "Jul 2026",              "Problem identification and requirement analysis",       "Completed"),
    ("Week 3",  "Jul-Aug 2026",          "Literature survey and related work study",              "Completed"),
    ("Week 4",  "Aug 2026",              "Dataset investigation and selection criteria",          "Completed"),
    ("Week 5",  "Aug 2026",              "HSLS:09 dataset acquisition and initial exploration",   "Completed"),
    ("Week 6",  "1-5 Sept 2026",         "Dataset cleaning and analysis",                        "Completed"),
    ("Week 7",  "14-19 Sept 2026",       "Feature engineering, correlation-based\nredundancy reduction, PCA evaluation",  "Completed"),
    ("Week 8",  "28 Sept - 3 Oct 2026",  "Class-weighted model comparison\nand CatBoost selection",                       "Completed"),
    ("Week 9",  "5-10 Oct 2026",         "Invalid-input handling, missing-data\nhandling, model evaluation",              "Completed"),
    ("Week 10", "19-24 Oct 2026",        "Flask backend development,\nquestionnaire-based recommendation engine",        "Completed"),
    ("Week 11", "Upcoming",              "Backend API testing and validation",                    "Planned"),
    ("Week 12", "Upcoming",              "Integration, bug fixing, recommendation\noutput verification",                  "Planned"),
    ("Week 13", "Upcoming",              "Final evaluation, documentation,\nproject demonstration preparation",          "Planned"),
]

rows_t = len(weeks) + 1
cols_t = 4
tbl2 = s6.shapes.add_table(rows_t, cols_t,
    Emu(CONTENT_LEFT - _in(0.15)), Emu(_in(2.05)),
    Emu(_in(8.6)), Emu(_in(4.75))).table

tbl2.columns[0].width = Emu(_in(0.85))
tbl2.columns[1].width = Emu(_in(1.8))
tbl2.columns[2].width = Emu(_in(4.65))
tbl2.columns[3].width = Emu(_in(1.3))

# Header
for c, hdr in enumerate(["Week", "Duration", "Activities", "Status"]):
    cell = tbl2.cell(0, c)
    set_cell(cell, hdr, Pt(9), True, WHITE, PP_ALIGN.CENTER)
    set_cell_fill(cell, DARK_BLUE)

status_colors = {"Completed": GREEN, "In Progress": AMBER, "Planned": RGBColor(0x70, 0x70, 0xD0), "Pending": RED_STATUS}

for r, (week, dur, act, status) in enumerate(weeks, start=1):
    set_cell(tbl2.cell(r, 0), week, Pt(8), True, BLACK, PP_ALIGN.CENTER)
    set_cell(tbl2.cell(r, 1), dur, Pt(7.5), False, BLACK, PP_ALIGN.LEFT)
    set_cell(tbl2.cell(r, 2), act, Pt(7.5), False, BLACK, PP_ALIGN.LEFT)
    sc = status_colors.get(status, BLACK)
    set_cell(tbl2.cell(r, 3), status, Pt(8), True, sc, PP_ALIGN.CENTER)
    if r % 2 == 0:
        for c2 in range(cols_t):
            set_cell_fill(tbl2.cell(r, c2), LIGHT_GRAY)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 7:  INDIVIDUAL CONTRIBUTION  ═════════
# ═══════════════════════════════════════════════════
s7 = build_content_slide("5. INDIVIDUAL CONTRIBUTION", 7)

ic_data = [
    ["Member", "Enrollment No.", "Key Contributions"],
    ["Rohit Prajapati", "241B211",
     "Dataset exploration and preprocessing,\n"
     "feature engineering, correlation analysis,\n"
     "dimensionality reduction, ML model\n"
     "evaluation and performance analysis"],
    ["Sai Arpit", "241B219",
     "Research and design of career recommendation\n"
     "approach, student profiling requirements,\n"
     "questionnaire and scenario design, career\n"
     "category definitions, relevance evaluation"],
    ["Samyak Jain", "241B222",
     "Flask backend development, questionnaire API\n"
     "implementation, response processing,\n"
     "recommendation scoring and ranking, career\n"
     "guide integration, skills and learning roadmaps"],
]

rows_ic = len(ic_data)
tbl3 = s7.shapes.add_table(rows_ic, 3,
    Emu(CONTENT_LEFT), Emu(_in(1.7)),
    Emu(_in(8.2)), Emu(_in(3.8))).table

tbl3.columns[0].width = Emu(_in(2.0))
tbl3.columns[1].width = Emu(_in(1.5))
tbl3.columns[2].width = Emu(_in(4.7))

for r in range(rows_ic):
    for c in range(3):
        cell = tbl3.cell(r, c)
        if r == 0:
            set_cell(cell, ic_data[r][c], Pt(11), True, WHITE, PP_ALIGN.CENTER)
            set_cell_fill(cell, DARK_BLUE)
        else:
            is_bold = (c < 2)
            al = PP_ALIGN.CENTER if c < 2 else PP_ALIGN.LEFT
            set_cell(cell, ic_data[r][c], Pt(10), is_bold, BLACK, al)
            if r % 2 == 0:
                set_cell_fill(cell, LIGHT_GRAY)

# Contribution area labels
labels = [
    ("Data and ML Pipeline", BLUE),
    ("Research and Design", RGBColor(0x00, 0x96, 0x88)),
    ("Backend Development", RGBColor(0x44, 0x72, 0xC4)),
]
x = _in(0.6)
for lbl, clr in labels:
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                   Emu(x), Emu(_in(5.8)), Emu(_in(2.7)), Emu(_in(0.4))) if False else \
            s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE,
                                Emu(x), Emu(_in(5.8)), Emu(_in(2.7)), Emu(_in(0.4)))
    shape.fill.solid()
    shape.fill.fore_color.rgb = clr
    shape.line.fill.background()
    tf = shape.text_frame
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run()
    run.text = lbl
    run.font.name = FONT_SANS
    run.font.size = Pt(10)
    run.font.bold = True
    run.font.color.rgb = WHITE
    x += _in(3.0)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 8:  DATASET  ═════════════════════════
# ═══════════════════════════════════════════════════
s8 = build_content_slide("6. WORK DONE (1/4) - Dataset and Selection", 8)

add_section_heading(s8, CONTENT_LEFT, _in(1.45), _in(4.2), "HSLS:09 Dataset")

add_bullet_list(s8, CONTENT_LEFT, _in(1.8), _in(4.2), _in(2.6), [
    "Name: High School Longitudinal Study of 2009",
    "Source: NCES, US Department of Education",
    "Type: Longitudinal educational dataset",
    "Cleaned rows: 14,668 students",
    "Cleaned columns: 854 features",
    "Feature inventory: 864 features catalogued",
    "Final model features: 170 (after selection)",
    "Target: X1STU30OCC2 (STEM vs Non-STEM)",
], font_size=Pt(10))

add_section_heading(s8, CONTENT_LEFT, _in(4.4), _in(4.2),
                    "Feature Categories", font_size=Pt(13))

add_bullet_list(s8, CONTENT_LEFT, _in(4.7), _in(4.2), _in(1.8), [
    "Academic performance (test scores, grades)",
    "STEM interest and self-efficacy measures",
    "Educational expectations and aspirations",
    "Parental education and occupation",
    "Engineered composite features (FE_ prefix)",
], font_size=Pt(10))

# Right side: Why HSLS:09
add_section_heading(s8, _in(5.3), _in(1.45), _in(4.2),
                    "Why HSLS:09 Was Selected")

add_bullet_list(s8, _in(5.3), _in(1.8), _in(4.2), _in(1.8), [
    "Authentic longitudinal student-level data",
    "Reliable government source (NCES)",
    "Relevant student-level features: academic performance,\n  STEM interests, self-efficacy, career outcomes",
    "Suitable for supervised ML classification",
    "Official documentation and codebooks available",
], font_size=Pt(10))

add_section_heading(s8, _in(5.3), _in(3.55), _in(4.2),
                    "Why Not Synthetic Data?", font_size=Pt(13))

add_bullet_list(s8, _in(5.3), _in(3.85), _in(4.2), _in(1.1), [
    "May not preserve genuine feature relationships",
    "Artificial patterns may not represent actual\n  student behaviour",
    "More suitable for software testing than\n  real-world model validation",
], font_size=Pt(10))

add_section_heading(s8, _in(5.3), _in(5.0), _in(4.2),
                    "Known Limitation", font_size=Pt(13))

add_textbox(s8, _in(5.3), _in(5.3), _in(4.2), _in(1.2),
    "HSLS:09 represents a US student population. Results cannot be "
    "directly generalised to Indian students without local validation. "
    "This dataset best matched the project's identified data requirements "
    "among the datasets investigated.",
    font_size=Pt(9), color=GRAY, font_name=FONT)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 9:  FEATURE ENGINEERING & ML  ════════
# ═══════════════════════════════════════════════════
s9 = build_content_slide("6. WORK DONE (2/4) - Feature Engineering and ML", 9)

add_section_heading(s9, CONTENT_LEFT, _in(1.45), _in(4.2), "Methodology")

add_bullet_list(s9, CONTENT_LEFT, _in(1.8), _in(4.0), _in(2.8), [
    "Feature selection from 854 available columns",
    "Composite feature engineering (student,\n  parent, counsellor, academic variables)",
    "Correlation analysis for redundancy reduction",
    "PCA evaluated for dimensionality reduction",
    "Class imbalance handled via class weighting",
    "Multiple classifiers trained and compared",
    "CatBoost selected as best performer",
], font_size=Pt(10.5))

add_textbox(s9, CONTENT_LEFT, _in(4.6), _in(4.2), _in(0.5),
    "Note: PCA was evaluated during the feature engineering\nphase. "
    "It is not part of the final model pipeline.",
    font_size=Pt(9), color=GRAY, font_name=FONT_SANS)

# Right side: ML Pipeline Flowchart
add_section_heading(s9, _in(5.3), _in(1.45), _in(4.0),
                    "ML Pipeline Flowchart", font_size=Pt(14))

flow_steps = [
    ("HSLS:09 Dataset\n(14,668 rows)", LIGHT_BLUE),
    ("Data Cleaning", LIGHT_GREEN),
    ("Feature Engineering\n(Composite Features)", LIGHT_GREEN),
    ("Correlation Analysis", LIGHT_GREEN),
    ("Feature Selection\n(170 Features)", LIGHT_GREEN),
    ("Train / Test Split", LIGHT_GREEN),
    ("Class-Weighted Training", LIGHT_ORANGE),
    ("Model Comparison", LIGHT_ORANGE),
    ("CatBoost Selected", LIGHT_BLUE),
    ("STEM / Non-STEM\nEstimate", LIGHT_BLUE),
]

y = _in(1.85)
bw = _in(2.8)
for i, (text, clr) in enumerate(flow_steps):
    bh = _in(0.42) if "\n" in text else _in(0.33)
    add_flowchart_box(s9, _in(5.8), y, bw, bh, text,
                      fill_color=clr, font_size=Pt(8))
    y += bh
    if i < len(flow_steps) - 1:
        add_down_arrow(s9, _in(5.8) + bw // 2, y, _in(0.12))
        y += _in(0.14)

# PCA label (side note)
add_flowchart_box(s9, _in(8.8), _in(2.7), _in(0.75), _in(0.4),
    "PCA\n(Evaluated)", fill_color=LIGHT_GRAY,
    text_color=GRAY, font_size=Pt(7), border_color=RGBColor(0xBF, 0xBF, 0xBF))


# ═══════════════════════════════════════════════════
# ═══  SLIDE 10:  MODEL RESULTS  ══════════════════
# ═══════════════════════════════════════════════════
s10 = build_content_slide("6. WORK DONE (3/4) - Model Results", 10)

add_section_heading(s10, CONTENT_LEFT, _in(1.45), _in(4.2),
                    "Model Comparison Results")

# Results table
res_data = [
    ["Model", "ROC-AUC", "Macro-F1"],
    ["CatBoost", "0.7248", "0.6114"],
    ["Random Forest", "0.6748", "0.4629"],
    ["Logistic Regression", "0.6611", "0.5693"],
]
tbl_r = s10.shapes.add_table(4, 3,
    Emu(CONTENT_LEFT), Emu(_in(1.85)),
    Emu(_in(4.0)), Emu(_in(1.5))).table
tbl_r.columns[0].width = Emu(_in(1.8))
tbl_r.columns[1].width = Emu(_in(1.1))
tbl_r.columns[2].width = Emu(_in(1.1))

for r in range(4):
    for c in range(3):
        cell = tbl_r.cell(r, c)
        if r == 0:
            set_cell(cell, res_data[r][c], Pt(10), True, WHITE, PP_ALIGN.CENTER)
            set_cell_fill(cell, DARK_BLUE)
        else:
            is_best = (r == 1)
            clr = GREEN if (is_best and c > 0) else BLACK
            set_cell(cell, res_data[r][c], Pt(10), is_best, clr,
                     PP_ALIGN.CENTER if c > 0 else PP_ALIGN.LEFT)
            if is_best:
                set_cell_fill(cell, LIGHT_GREEN)

add_section_heading(s10, CONTENT_LEFT, _in(3.5), _in(4.2),
                    "Additional CatBoost Metrics", font_size=Pt(13))

add_bullet_list(s10, CONTENT_LEFT, _in(3.8), _in(4.0), _in(1.2), [
    "PR-AUC: 0.40 (Baseline: 0.166)",
    "STEM recall: 57% (up from 11% before\n  class weighting)",
    "Features used: 170",
], font_size=Pt(10.5))

add_section_heading(s10, CONTENT_LEFT, _in(5.0), _in(4.2),
                    "Why CatBoost?", font_size=Pt(13))

add_bullet_list(s10, CONTENT_LEFT, _in(5.3), _in(4.0), _in(1.2), [
    "Highest ROC-AUC among compared models",
    "Native handling of missing values",
    "Balanced STEM recall with class weighting",
], font_size=Pt(10.5))

# Right side: editable charts
add_section_heading(s10, _in(5.3), _in(1.45), _in(4.0),
                    "ROC-AUC Comparison", font_size=Pt(14))

cd1 = CategoryChartData()
cd1.categories = ['CatBoost', 'Random\nForest', 'Logistic\nRegression']
cd1.add_series('ROC-AUC', (0.7248, 0.6748, 0.6611))
chart_frame1 = s10.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Emu(_in(5.2)), Emu(_in(1.85)), Emu(_in(4.2)), Emu(_in(2.1)), cd1)
ch1 = chart_frame1.chart
ch1.has_legend = False
ser1 = ch1.plots[0].series[0]
ser1.format.fill.solid()
ser1.format.fill.fore_color.rgb = BLUE
ser1.has_data_labels = True
ser1.data_labels.font.size = Pt(9)
ser1.data_labels.number_format = '0.0000'
ser1.data_labels.label_position = XL_LABEL_POSITION.OUTSIDE_END

add_section_heading(s10, _in(5.3), _in(4.1), _in(4.0),
                    "Macro-F1 Comparison", font_size=Pt(14))

cd2 = CategoryChartData()
cd2.categories = ['CatBoost', 'Random\nForest', 'Logistic\nRegression']
cd2.add_series('Macro-F1', (0.6114, 0.4629, 0.5693))
chart_frame2 = s10.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
    Emu(_in(5.2)), Emu(_in(4.45)), Emu(_in(4.2)), Emu(_in(2.0)), cd2)
ch2 = chart_frame2.chart
ch2.has_legend = False
ser2 = ch2.plots[0].series[0]
ser2.format.fill.solid()
ser2.format.fill.fore_color.rgb = RGBColor(0x44, 0x72, 0xC4)
ser2.has_data_labels = True
ser2.data_labels.font.size = Pt(9)
ser2.data_labels.number_format = '0.0000'
ser2.data_labels.label_position = XL_LABEL_POSITION.OUTSIDE_END

# Disclaimer
add_textbox(s10, CONTENT_LEFT, _in(6.5), _in(8.5), _in(0.3),
    "Note: Model has moderate predictive performance. It estimates alignment with "
    "self-reported STEM aspiration. It does not determine or guarantee career outcomes.",
    font_size=Pt(8), color=GRAY, font_name=FONT_SANS)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 11:  BACKEND & UML  ══════════════════
# ═══════════════════════════════════════════════════
s11 = build_content_slide("6. WORK DONE (4/4) - Backend and UML", 11)

# ── COMPONENT DIAGRAM (Top Left) ──
add_section_heading(s11, _in(0.35), _in(1.35), _in(4.5),
                    "Component Diagram", font_size=Pt(11))

# System boundary
sys_box = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE,
    Emu(_in(0.3)), Emu(_in(1.65)), Emu(_in(4.5)), Emu(_in(2.0)))
sys_box.fill.solid()
sys_box.fill.fore_color.rgb = RGBColor(0xF8, 0xF8, 0xF8)
sys_box.line.color.rgb = DARK_BLUE
sys_box.line.width = Pt(1)

add_textbox(s11, _in(0.4), _in(1.67), _in(2.0), _in(0.17),
            "Flask Backend System", font_size=Pt(7), bold=True,
            color=DARK_BLUE, font_name=FONT_SANS)

comp_boxes = [
    ("app.py\n(Main App)", _in(0.45), _in(1.9)),
    ("CatBoost\nModel", _in(1.75), _in(1.9)),
    ("Metadata\n(.joblib)", _in(3.0), _in(1.9)),
    ("questionnaire.py\n(Blueprint)", _in(0.45), _in(2.6)),
    ("Scoring\nEngine", _in(1.75), _in(2.6)),
    ("Career\nGuides", _in(3.0), _in(2.6)),
]
for txt, lf, tp in comp_boxes:
    add_flowchart_box(s11, lf, tp, _in(1.15), _in(0.5), txt,
                      fill_color=LIGHT_BLUE, font_size=Pt(6.5))

# API endpoints
add_flowchart_box(s11, _in(0.45), _in(3.25), _in(4.15), _in(0.3),
    "GET /  |  GET /health  |  GET /features  |  POST /predict  |  GET /questionnaire  |  POST /profile",
    fill_color=LIGHT_GREEN, font_size=Pt(6), border_color=GREEN)

# ── SEQUENCE DIAGRAM (Top Right) ──
add_section_heading(s11, _in(5.1), _in(1.35), _in(4.5),
                    "Sequence Diagram", font_size=Pt(11))

participants = [
    ("Student", _in(5.2)),
    ("Frontend", _in(6.05)),
    ("Flask\nAPI", _in(6.9)),
    ("Quest.\nModule", _in(7.75)),
    ("Career\nGuides", _in(8.6)),
]
for name, left in participants:
    box = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Emu(left), Emu(_in(1.65)), Emu(_in(0.7)), Emu(_in(0.4)))
    box.fill.solid()
    box.fill.fore_color.rgb = DARK_BLUE
    box.line.fill.background()
    tf = box.text_frame
    tf.word_wrap = True
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    run = tf.paragraphs[0].add_run()
    run.text = name
    run.font.name = FONT_SANS
    run.font.size = Pt(6)
    run.font.bold = True
    run.font.color.rgb = WHITE

# Lifelines
for _, left in participants:
    line = s11.shapes.add_shape(MSO_SHAPE.RECTANGLE,
        Emu(left + _in(0.33)), Emu(_in(2.07)), Emu(_in(0.03)), Emu(_in(1.55)))
    line.fill.solid()
    line.fill.fore_color.rgb = RGBColor(0xBF, 0xBF, 0xBF)
    line.line.fill.background()

# Sequence messages
seq_msgs = [
    ("Answers 30 Qs",   _in(5.55), _in(6.4),  _in(2.15)),
    ("POST /profile",   _in(6.4),  _in(7.25), _in(2.28)),
    ("Process answers", _in(7.25), _in(8.1),  _in(2.41)),
    ("Get career data", _in(8.1),  _in(8.95), _in(2.54)),
    ("Career guides",   _in(8.95), _in(8.1),  _in(2.67)),  # reverse
    ("Recommendations", _in(8.1),  _in(7.25), _in(2.80)),  # reverse
    ("JSON response",   _in(7.25), _in(6.4),  _in(2.93)),  # reverse
    ("Display results", _in(6.4),  _in(5.55), _in(3.06)),  # reverse
]
for label, sx, ex, y in seq_msgs:
    is_rev = ex < sx
    al = min(sx, ex)
    aw = abs(ex - sx)
    arrow_type = MSO_SHAPE.LEFT_ARROW if is_rev else MSO_SHAPE.RIGHT_ARROW
    arr = s11.shapes.add_shape(arrow_type,
        Emu(al), Emu(y), Emu(aw), Emu(_in(0.06)))
    arr.fill.solid()
    arr.fill.fore_color.rgb = DARK_BLUE if not is_rev else RGBColor(0x00, 0x96, 0x88)
    arr.line.fill.background()
    add_textbox(s11, al, y - _in(0.12), aw, _in(0.12),
                label, font_size=Pt(5), color=BLACK,
                font_name=FONT_SANS, alignment=PP_ALIGN.CENTER)

# ── RECOMMENDATION FLOW (Bottom) ──
add_section_heading(s11, _in(0.3), _in(3.75), _in(9.0),
                    "Questionnaire Recommendation Flow", font_size=Pt(11))

flow_items = [
    ("Receive\n30 Answers", LIGHT_ORANGE),
    ("Validate\nAnswers", LIGHT_ORANGE),
    ("Separate\n3 Groups", LIGHT_GREEN),
    ("Interest\nScores", LIGHT_GREEN),
    ("Logical\nReasoning %", LIGHT_GREEN),
    ("Scenario\nScores", LIGHT_GREEN),
    ("Rank Career\nCategories", LIGHT_BLUE),
    ("Select\nGuides", LIGHT_BLUE),
    ("Generate\nRoadmaps", LIGHT_BLUE),
    ("Return\nJSON", PURPLE_LIGHT),
]
x = _in(0.15)
for i, (text, clr) in enumerate(flow_items):
    bw_f = _in(0.87)
    add_flowchart_box(s11, x, _in(4.05), bw_f, _in(0.5), text,
                      fill_color=clr, font_size=Pt(6))
    x += bw_f
    if i < len(flow_items) - 1:
        arr = s11.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW,
            Emu(x), Emu(_in(4.25)), Emu(_in(0.1)), Emu(_in(0.08)))
        arr.fill.solid()
        arr.fill.fore_color.rgb = DARK_BLUE
        arr.line.fill.background()
        x += _in(0.1)

# ── BACKEND DETAILS (Bottom) ──
add_section_heading(s11, _in(0.3), _in(4.7), _in(4.5),
                    "Backend Implementation", font_size=Pt(10))

add_bullet_list(s11, _in(0.3), _in(4.95), _in(4.6), _in(1.8), [
    "GET /questionnaire: 30 questions (3 sections)",
    "POST /profile: accepts answers, returns recommendations",
    "Answer validation: all 30 answers required (a/b/c/d)",
    "Interest scoring: 7 categories (analytical, creative, etc.)",
    "Logical reasoning: correct/total percentage",
    "Weighted ranking: 65% personal + 35% scenario",
    "Output: top 3 careers with explanations, skills, roadmaps",
], font_size=Pt(7.5), font_name=FONT_SANS)

add_section_heading(s11, _in(5.1), _in(4.7), _in(4.5),
                    "CatBoost Prediction Endpoint", font_size=Pt(10))

add_bullet_list(s11, _in(5.1), _in(4.95), _in(4.6), _in(1.5), [
    "POST /predict: accepts 170 features as JSON",
    "Validates all required features present",
    "Handles missing values (null to NaN)",
    "Rejects booleans and infinite values",
    "Returns: STEM/Non-STEM, probability, note",
], font_size=Pt(7.5), font_name=FONT_SANS)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 12:  WORK TO BE DONE  ════════════════
# ═══════════════════════════════════════════════════
s12 = build_content_slide("7. WORK TO BE DONE", 12)

add_section_heading(s12, CONTENT_LEFT, _in(1.45), _in(8.5),
                    "Remaining Tasks (Weeks 11-13)")

# Week 11
add_textbox(s12, CONTENT_LEFT, _in(1.9), _in(1.2), _in(0.25),
            "WEEK 11", font_size=Pt(12), bold=True, color=HEADING_BLUE)
add_textbox(s12, _in(1.8), _in(1.9), _in(1.5), _in(0.25),
            "(Planned)", font_size=Pt(10), bold=True, color=RGBColor(0x70, 0x70, 0xD0))
add_bullet_list(s12, CONTENT_LEFT, _in(2.2), _in(4.0), _in(1.0), [
    "Backend API testing with valid and invalid inputs",
    "Input validation and edge-case testing",
    "Error handling and response format verification",
], font_size=Pt(10))

# Week 12
add_textbox(s12, CONTENT_LEFT, _in(3.2), _in(1.2), _in(0.25),
            "WEEK 12", font_size=Pt(12), bold=True, color=HEADING_BLUE)
add_textbox(s12, _in(1.8), _in(3.2), _in(1.5), _in(0.25),
            "(Planned)", font_size=Pt(10), bold=True, color=RGBColor(0x70, 0x70, 0xD0))
add_bullet_list(s12, CONTENT_LEFT, _in(3.5), _in(4.0), _in(1.0), [
    "Recommendation scoring validation",
    "Frontend-backend integration testing",
    "Bug fixing and reliability checks",
], font_size=Pt(10))

# Week 13
add_textbox(s12, CONTENT_LEFT, _in(4.5), _in(1.2), _in(0.25),
            "WEEK 13", font_size=Pt(12), bold=True, color=HEADING_BLUE)
add_textbox(s12, _in(1.8), _in(4.5), _in(1.5), _in(0.25),
            "(Planned)", font_size=Pt(10), bold=True, color=RGBColor(0x70, 0x70, 0xD0))
add_bullet_list(s12, CONTENT_LEFT, _in(4.8), _in(4.0), _in(1.0), [
    "Final evaluation and performance analysis",
    "Documentation and report preparation",
    "Project demonstration preparation",
], font_size=Pt(10))

# Right side: status overview
add_section_heading(s12, _in(5.3), _in(1.9), _in(4.2),
                    "Task Status Overview", font_size=Pt(14))

status_items = [
    ("Backend API testing", "Pending"),
    ("Input validation testing", "Pending"),
    ("Recommendation scoring validation", "Pending"),
    ("Answer pattern testing", "Pending"),
    ("Frontend-backend integration", "Pending"),
    ("Bug fixing and reliability", "Pending"),
    ("Documentation", "Pending"),
    ("Project demonstration", "Pending"),
]
sy = _in(2.3)
for task, status in status_items:
    # Status dot
    dot = s12.shapes.add_shape(MSO_SHAPE.OVAL,
        Emu(_in(5.4)), Emu(sy + _in(0.05)), Emu(_in(0.12)), Emu(_in(0.12)))
    dot.fill.solid()
    dot.fill.fore_color.rgb = RED_STATUS
    dot.line.fill.background()
    add_textbox(s12, _in(5.6), sy, _in(2.8), _in(0.22),
                task, font_size=Pt(9), color=BLACK, font_name=FONT_SANS)
    add_textbox(s12, _in(8.5), sy, _in(0.9), _in(0.22),
                status, font_size=Pt(8), bold=True, color=RED_STATUS,
                font_name=FONT_SANS, alignment=PP_ALIGN.CENTER)
    sy += _in(0.35)

add_textbox(s12, _in(5.3), _in(5.4), _in(4.2), _in(0.4),
    "Backend testing is the immediate next milestone.\nAll items above remain pending.",
    font_size=Pt(9), color=GRAY, font_name=FONT_SANS)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 13:  CONCLUSION  ═════════════════════
# ═══════════════════════════════════════════════════
s13 = build_content_slide("8. CONCLUSION", 13)

add_section_heading(s13, CONTENT_LEFT, _in(1.45), _in(8.5),
                    "Summary of Progress")

completed = [
    "HSLS:09 dataset analysed and prepared (14,668 students, 854 features)",
    "Feature engineering: composite features created, correlation analysis performed",
    "Dimensionality reduction explored (PCA evaluated, correlation-based selection applied)",
    "CatBoost selected after comparison with Random Forest and Logistic Regression",
    "Class weighting applied to handle STEM minority class imbalance",
    "30-question career exploration questionnaire designed (personal, logical, scenario)",
    "Flask backend developed with prediction and recommendation endpoints",
    "Career recommendations include explanations, skills, projects and 4-week roadmaps",
]

y = _in(1.85)
for item in completed:
    add_textbox(s13, CONTENT_LEFT, y, _in(0.25), _in(0.22),
                "\u2713", font_size=Pt(12), bold=True, color=GREEN)
    add_textbox(s13, CONTENT_LEFT + _in(0.3), y, _in(8.0), _in(0.25),
                item, font_size=Pt(10.5), color=BLACK)
    y += _in(0.38)

add_section_heading(s13, CONTENT_LEFT, _in(5.05), _in(8.5),
                    "Next Milestone", font_size=Pt(14))

add_textbox(s13, CONTENT_LEFT, _in(5.35), _in(8.5), _in(0.25),
            "\u25B6  Backend testing remains the immediate next step.",
            font_size=Pt(11), color=BLACK)

add_section_heading(s13, CONTENT_LEFT, _in(5.75), _in(8.5),
                    "Expected Outcome", font_size=Pt(14))

add_textbox(s13, CONTENT_LEFT, _in(6.05), _in(8.5), _in(0.6),
    "A system combining educational data-based STEM estimation with questionnaire-based "
    "career exploration, providing students with personalised career suggestions, "
    "explanations and learning guidance.",
    font_size=Pt(10.5), color=BLACK)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 14:  REFERENCES  ═════════════════════
# ═══════════════════════════════════════════════════
s14 = build_content_slide("9. REFERENCES (IEEE Format)", 14)

refs = [
    '[1]  National Center for Education Statistics, "High School Longitudinal Study of '
    '2009 (HSLS:09)," U.S. Department of Education, Institute of Education Sciences. '
    '[Online]. Available: https://nces.ed.gov/surveys/hsls09/',

    '[2]  H. Gardner, Frames of Mind: The Theory of Multiple Intelligences. '
    'New York, NY, USA: Basic Books, 1983.',

    '[3]  L. Prokhorenkova, G. Gusev, A. Vorobev, A. V. Dorogush, and A. Gulin, '
    '"CatBoost: Unbiased boosting with categorical features," in Proc. Adv. Neural '
    'Inf. Process. Syst. (NeurIPS), vol. 31, 2018, pp. 6638-6648.',

    '[4]  C. Romero and S. Ventura, "Educational data mining and learning analytics: '
    'An updated survey," WIREs Data Mining Knowl. Discov., vol. 10, no. 3, e1355, 2020.',

    '[5]  R. S. J. d. Baker and K. Yacef, "The state of educational data mining in '
    '2009: A review and future visions," J. Educ. Data Mining, vol. 1, no. 1, pp. 3-17, 2009.',

    '[6]  X. Wang, "Why students choose STEM majors: Motivation, high school learning, '
    'and postsecondary context of support," Amer. Educ. Res. J., vol. 50, no. 5, '
    'pp. 1081-1121, 2013.',

    '[7]  Flask Web Development Framework. [Online]. Available: '
    'https://flask.palletsprojects.com/',
]

y = _in(1.6)
for ref in refs:
    add_textbox(s14, CONTENT_LEFT, y, _in(8.3), _in(0.65),
                ref, font_size=Pt(9), color=BLACK)
    y += _in(0.68)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 15:  SCOPE CLARIFICATION  ════════════
# ═══════════════════════════════════════════════════
s15 = build_content_slide("CURRENT IMPLEMENTATION AND FUTURE SCOPE", 15)

# Left: Current implementation
add_section_heading(s15, CONTENT_LEFT, _in(1.45), _in(4.0),
                    "Current Implementation")

add_bullet_list(s15, CONTENT_LEFT, _in(1.85), _in(4.0), _in(2.5), [
    "Questionnaire-based student profiling",
    "30 questions across 3 sections",
    "Educational data-based STEM/Non-STEM model",
    "CatBoost classifier with 170 features",
    "Career recommendations with match explanations",
    "Skills, beginner projects and 4-week roadmaps",
    "Flask backend with RESTful API endpoints",
], font_size=Pt(10.5))

# Right: Not implemented
add_section_heading(s15, _in(5.3), _in(1.45), _in(4.2),
                    "Not Implemented in Current Version")

add_bullet_list(s15, _in(5.3), _in(1.85), _in(4.0), _in(1.5), [
    "Resume upload functionality",
    "PDF resume parsing",
    "Automated resume information extraction",
    "OCR-based document processing",
], font_size=Pt(10.5), color=RED_STATUS)

# Future extensions
add_section_heading(s15, _in(5.3), _in(3.3), _in(4.2),
                    "Future Extensions")

add_bullet_list(s15, _in(5.3), _in(3.7), _in(4.0), _in(2.0), [
    "Resume upload and PDF parsing",
    "Extract education, skills, experience from resumes",
    "Combine extracted resume data with career\n  recommendation logic",
    "Validate with appropriate Indian student data",
    "Frontend-backend integration and deployment",
], font_size=Pt(10.5))

# Bottom note
add_textbox(s15, CONTENT_LEFT, _in(5.7), _in(8.5), _in(0.8),
    "The project scope evolved from the initial title towards a structured student-profiling "
    "and educational-data-based approach. The questionnaire-based system captures student "
    "interests, reasoning ability and situational responses, providing a foundation that can "
    "be extended with resume-based features in future iterations.",
    font_size=Pt(10), color=GRAY)


# ═══════════════════════════════════════════════════
# ═══  SLIDE 16:  THANK YOU  ══════════════════════
# ═══════════════════════════════════════════════════
s16 = prs.slides.add_slide(title_only_layout)

# Large university logo (centre-top)
if LARGE_LOGO_PATH:
    s16.shapes.add_picture(LARGE_LOGO_PATH,
                           Emu(3657600), Emu(152400), Emu(1215436), Emu(1447799))

# Thank You text
add_textbox(s16, _in(2.5), _in(3.2), _in(5.0), _in(0.9),
            "Thank You",
            font_size=Pt(48), bold=True, color=BLACK,
            alignment=PP_ALIGN.CENTER)

# Project title
add_textbox(s16, _in(1.5), _in(4.3), _in(7.0), _in(0.5),
            "AI-Based Resume Analyzer and Career Recommendation System",
            font_size=Pt(14), color=GRAY,
            alignment=PP_ALIGN.CENTER)

# Team and guide
add_textbox(s16, _in(1.5), _in(5.0), _in(7.0), _in(0.4),
            "Rohit Prajapati (241B211)   |   Sai Arpit (241B219)   |   Samyak Jain (241B222)",
            font_size=Pt(11), color=BLACK,
            alignment=PP_ALIGN.CENTER)

add_textbox(s16, _in(1.5), _in(5.4), _in(7.0), _in(0.3),
            "Project Guide: Dr. Prateek Pandey",
            font_size=Pt(11), color=GRAY,
            alignment=PP_ALIGN.CENTER)

add_textbox(s16, _in(1.5), _in(5.8), _in(7.0), _in(0.3),
            "Jaypee University of Engineering & Technology, Guna (M.P.)",
            font_size=Pt(12), bold=False, color=DARK_BLUE,
            alignment=PP_ALIGN.CENTER)

# Slide number box (large, matching original Thank You slide)
txBox16 = s16.shapes.add_textbox(Emu(0), Emu(1600200), Emu(1295400), Emu(990600))
sp16 = txBox16._element
spPr16 = sp16.find(".//{http://schemas.openxmlformats.org/drawingml/2006/main}spPr")
if spPr16 is None:
    spPr16 = etree.SubElement(sp16,
        "{http://schemas.openxmlformats.org/drawingml/2006/main}spPr")
sf16 = etree.SubElement(spPr16,
    "{http://schemas.openxmlformats.org/drawingml/2006/main}solidFill")
clr16 = etree.SubElement(sf16,
    "{http://schemas.openxmlformats.org/drawingml/2006/main}srgbClr")
clr16.set("val", NUM_FILL)
tf16 = txBox16.text_frame
tf16.paragraphs[0].alignment = PP_ALIGN.CENTER
run16 = tf16.paragraphs[0].add_run()
run16.text = "16"
run16.font.name = FONT
run16.font.size = Pt(24)
run16.font.bold = True
run16.font.color.rgb = WHITE


# ═══════════════════════════════════════════════════
# SAVE
# ═══════════════════════════════════════════════════
prs.save(str(OUT_PPT))
print(f"\nPresentation saved to: {OUT_PPT}")
print(f"Total slides: {len(prs.slides)}")

# Verify
prs2 = Presentation(str(OUT_PPT))
print(f"Verified slide count: {len(prs2.slides)}")
for i, sl in enumerate(prs2.slides):
    texts = []
    for shape in sl.shapes:
        if shape.has_text_frame:
            for p in shape.text_frame.paragraphs:
                t = p.text.strip()
                if t and len(t) > 3:
                    texts.append(t[:60])
                    break
            if texts:
                break
    title = texts[0] if texts else "(no text)"
    print(f"  Slide {i+1:2d}: {len(sl.shapes):3d} shapes | {title}")
