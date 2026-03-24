from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.platypus import Paragraph
from reportlab.pdfgen import canvas


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output" / "pdf"
OUTPUT_FILE = OUTPUT_DIR / "todo-app-code-infographic.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4

BG = colors.HexColor("#F5EFE4")
CARD = colors.HexColor("#FFF9F0")
CARD_ALT = colors.HexColor("#F8F1E7")
INK = colors.HexColor("#1F2A1F")
MUTED = colors.HexColor("#5F6D62")
ACCENT = colors.HexColor("#C65D2E")
ACCENT_DARK = colors.HexColor("#8E3D1C")
SUCCESS = colors.HexColor("#2F7D4B")
LINE = colors.HexColor("#D7CCBC")
SOFT_GREEN = colors.HexColor("#DFECE3")
SOFT_ORANGE = colors.HexColor("#F6E1D6")
SOFT_GOLD = colors.HexColor("#EFE3BF")


styles = getSampleStyleSheet()
TITLE_STYLE = ParagraphStyle(
    "Title",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=26,
    leading=30,
    textColor=INK,
)
SUBTITLE_STYLE = ParagraphStyle(
    "Subtitle",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=11,
    leading=15,
    textColor=MUTED,
)
SECTION_STYLE = ParagraphStyle(
    "Section",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=15,
    leading=18,
    textColor=INK,
)
BODY_STYLE = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    textColor=INK,
)
SMALL_STYLE = ParagraphStyle(
    "Small",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    textColor=MUTED,
)
TAG_STYLE = ParagraphStyle(
    "Tag",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=9,
    leading=11,
    textColor=ACCENT_DARK,
)


def draw_wrapped_paragraph(pdf, text, style, x, y_top, width):
    paragraph = Paragraph(text, style)
    _, height = paragraph.wrap(width, PAGE_HEIGHT)
    paragraph.drawOn(pdf, x, y_top - height)
    return height


def draw_round_rect(pdf, x, y, width, height, fill_color, stroke_color=LINE, radius=16):
    pdf.setFillColor(fill_color)
    pdf.setStrokeColor(stroke_color)
    pdf.roundRect(x, y, width, height, radius, stroke=1, fill=1)


def draw_tag(pdf, x, y, label, fill_color=SOFT_ORANGE):
    text_width = stringWidth(label, "Helvetica-Bold", 9)
    width = text_width + 16
    height = 18
    draw_round_rect(pdf, x, y - height + 2, width, height, fill_color, fill_color, radius=8)
    pdf.setFillColor(ACCENT_DARK)
    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(x + 8, y - 10, label)
    return width


def draw_card(pdf, x, y, width, height, title, body, fill_color=CARD, tag=None):
    draw_round_rect(pdf, x, y, width, height, fill_color)
    current_y = y + height - 18
    if tag:
        draw_tag(pdf, x + 14, current_y, tag)
        current_y -= 24
    pdf.setFillColor(INK)
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(x + 14, current_y, title)
    current_y -= 8
    draw_wrapped_paragraph(pdf, body, BODY_STYLE, x + 14, current_y - 6, width - 28)


def draw_arrow(pdf, x1, y1, x2, y2, label=None):
    pdf.setStrokeColor(ACCENT)
    pdf.setLineWidth(2)
    pdf.line(x1, y1, x2, y2)
    angle = 6
    if x2 >= x1:
        pdf.line(x2, y2, x2 - angle, y2 + 4)
        pdf.line(x2, y2, x2 - angle, y2 - 4)
    else:
        pdf.line(x2, y2, x2 + angle, y2 + 4)
        pdf.line(x2, y2, x2 + angle, y2 - 4)
    if label:
        pdf.setFillColor(ACCENT_DARK)
        pdf.setFont("Helvetica-Bold", 9)
        pdf.drawCentredString((x1 + x2) / 2, y1 + 8, label)


def setup_page(pdf, page_number):
    pdf.setFillColor(BG)
    pdf.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor("#EED4C6"))
    pdf.circle(PAGE_WIDTH - 30 * mm, PAGE_HEIGHT - 22 * mm, 20 * mm, stroke=0, fill=1)
    pdf.setFillColor(colors.HexColor("#DDE9DF"))
    pdf.circle(24 * mm, 28 * mm, 18 * mm, stroke=0, fill=1)
    pdf.setFillColor(MUTED)
    pdf.setFont("Helvetica", 9)
    pdf.drawRightString(PAGE_WIDTH - 18 * mm, 12 * mm, f"Page {page_number}")


def page_one(pdf):
    setup_page(pdf, 1)
    x = 18 * mm
    y = PAGE_HEIGHT - 20 * mm

    draw_tag(pdf, x, y, "Beginner guide", SOFT_GOLD)
    title_top = y - 14
    title_height = draw_wrapped_paragraph(
        pdf,
        "How the Python To-Do Web App Works",
        TITLE_STYLE,
        x,
        title_top,
        125 * mm,
    )
    draw_wrapped_paragraph(
        pdf,
        "This infographic explains the files, the request flow, and the reason each piece exists. It is written for someone new to Flask, HTML, and JavaScript.",
        SUBTITLE_STYLE,
        x,
        title_top - title_height - 6,
        140 * mm,
    )

    arch_y = PAGE_HEIGHT - 116 * mm
    box_w = 48 * mm
    box_h = 30 * mm
    start_x = 22 * mm
    gap = 12 * mm

    draw_card(
        pdf,
        start_x,
        arch_y,
        box_w,
        box_h,
        "Browser UI",
        "The user sees the page, types tasks, clicks buttons, and reads updates.",
        SOFT_ORANGE,
        "HTML + CSS + JS",
    )
    draw_card(
        pdf,
        start_x + box_w + gap,
        arch_y,
        box_w,
        box_h,
        "Flask Server",
        "Python receives requests, decides what to do, and returns JSON or HTML.",
        SOFT_GREEN,
        "app.py",
    )
    draw_card(
        pdf,
        start_x + 2 * (box_w + gap),
        arch_y,
        box_w,
        box_h,
        "tasks.json",
        "Server-side storage. Tasks stay on disk instead of living only in the browser.",
        CARD_ALT,
        "Data file",
    )
    draw_arrow(pdf, start_x + box_w, arch_y + box_h / 2, start_x + box_w + gap - 3, arch_y + box_h / 2, "HTTP")
    draw_arrow(
        pdf,
        start_x + 2 * box_w + gap,
        arch_y + box_h / 2,
        start_x + 2 * box_w + 2 * gap - 3,
        arch_y + box_h / 2,
        "read / write",
    )

    draw_card(
        pdf,
        18 * mm,
        34 * mm,
        82 * mm,
        62 * mm,
        "What the project contains",
        "<b>app.py</b> - Flask routes and JSON storage logic.<br/>"
        "<b>templates/index.html</b> - page structure sent by Flask.<br/>"
        "<b>static/app.js</b> - button clicks, fetch calls, DOM updates.<br/>"
        "<b>static/styles.css</b> - layout, colors, typography, mobile styles.<br/>"
        "<b>tasks.json</b> - saved task data.<br/>"
        "<b>requirements.txt</b> - Python dependency list.",
        CARD,
        "Files",
    )
    draw_card(
        pdf,
        106 * mm,
        34 * mm,
        86 * mm,
        62 * mm,
        "One sentence summary",
        "The app is a simple full-stack project: HTML shows the screen, JavaScript talks to the server, Flask handles the logic in Python, and a JSON file stores the tasks.",
        CARD,
        "Big picture",
    )


def page_two(pdf):
    setup_page(pdf, 2)
    x = 18 * mm
    y = PAGE_HEIGHT - 20 * mm
    draw_tag(pdf, x, y, "Code walkthrough", SOFT_GOLD)
    title_top = y - 14
    title_height = draw_wrapped_paragraph(
        pdf,
        "Backend and frontend responsibilities",
        TITLE_STYLE,
        x,
        title_top,
        150 * mm,
    )
    draw_wrapped_paragraph(
        pdf,
        "Read this page from left to right: Python runs the server, then the browser code uses that server.",
        SUBTITLE_STYLE,
        x,
        title_top - title_height - 6,
        150 * mm,
    )

    left_x = 18 * mm
    right_x = 108 * mm
    top_y = PAGE_HEIGHT - 100 * mm
    card_w = 84 * mm
    card_h = 42 * mm

    draw_card(
        pdf,
        left_x,
        top_y,
        card_w,
        card_h,
        "1. app.py starts Flask",
        "Flask creates the web server. The variable <b>app = Flask(__name__)</b> tells Python to serve pages, templates, and API routes.",
        SOFT_GREEN,
        "Python core",
    )
    draw_card(
        pdf,
        left_x,
        top_y - 48 * mm,
        card_w,
        card_h,
        "2. Helper functions manage data",
        "<b>load_tasks()</b> opens <b>tasks.json</b> and returns a safe list. "
        "<b>save_tasks()</b> writes the latest task list back to disk.",
        CARD,
        "Persistence",
    )
    draw_card(
        pdf,
        left_x,
        top_y - 96 * mm,
        card_w,
        card_h,
        "3. API routes define actions",
        "<b>GET /api/tasks</b> sends all tasks. "
        "<b>POST</b> adds a task. "
        "<b>PATCH</b> updates a task. "
        "<b>DELETE</b> removes one task or clears completed ones.",
        SOFT_ORANGE,
        "Backend API",
    )

    draw_card(
        pdf,
        right_x,
        top_y,
        card_w,
        card_h,
        "4. index.html builds the screen",
        "The template defines the heading, text box, add button, counter, empty state, and task list container that JavaScript will fill later.",
        CARD,
        "Template",
    )
    draw_card(
        pdf,
        right_x,
        top_y - 48 * mm,
        card_w,
        card_h,
        "5. app.js makes the page interactive",
        "JavaScript listens for clicks and form submits, calls <b>fetch()</b>, and redraws the task list after the server responds.",
        SOFT_GOLD,
        "Browser logic",
    )
    draw_card(
        pdf,
        right_x,
        top_y - 96 * mm,
        card_w,
        card_h,
        "6. styles.css shapes the experience",
        "CSS adds the warm background, card layout, buttons, spacing, completed-task styling, and mobile adjustments.",
        CARD_ALT,
        "Presentation",
    )

    draw_arrow(pdf, 101 * mm, top_y + 21 * mm, 109 * mm, top_y + 21 * mm)
    draw_arrow(pdf, 101 * mm, top_y - 27 * mm, 109 * mm, top_y - 27 * mm)
    draw_arrow(pdf, 101 * mm, top_y - 75 * mm, 109 * mm, top_y - 75 * mm)


def page_three(pdf):
    setup_page(pdf, 3)
    x = 18 * mm
    y = PAGE_HEIGHT - 20 * mm
    draw_tag(pdf, x, y, "Request lifecycle", SOFT_GOLD)
    title_top = y - 14
    title_height = draw_wrapped_paragraph(
        pdf,
        "What happens when a beginner clicks 'Add Task'?",
        TITLE_STYLE,
        x,
        title_top,
        155 * mm,
    )
    draw_wrapped_paragraph(
        pdf,
        "This is the easiest way to understand a full-stack app: follow one action from the browser to the server and back.",
        SUBTITLE_STYLE,
        x,
        title_top - title_height - 6,
        150 * mm,
    )

    steps = [
        ("1", "User types a task", "The browser stores the text in the input box inside the HTML form."),
        ("2", "JavaScript intercepts submit", "app.js prevents a full page reload and sends the text to the Flask API with fetch()."),
        ("3", "Flask validates input", "app.py checks that the title is not empty. If it is empty, the server returns an error."),
        ("4", "Python saves data", "Flask creates a task id, adds a new dictionary to the list, and writes the list into tasks.json."),
        ("5", "Server responds with JSON", "The new task comes back to the browser as structured data, not as plain text."),
        ("6", "JavaScript redraws the list", "The browser updates the DOM so the new task appears immediately on screen."),
    ]

    card_x_positions = [22 * mm, 110 * mm]
    card_w = 78 * mm
    card_h = 30 * mm
    gap_y = 10 * mm
    top_cards_y = PAGE_HEIGHT - 98 * mm

    for index, (number, title, body) in enumerate(steps):
        row = index // 2
        col = index % 2
        x_pos = card_x_positions[col]
        y_pos = top_cards_y - row * (card_h + gap_y)
        draw_round_rect(pdf, x_pos, y_pos, card_w, card_h, CARD)
        pdf.setFillColor(ACCENT)
        pdf.circle(x_pos + 10, y_pos + card_h - 10, 9, stroke=0, fill=1)
        pdf.setFillColor(colors.white)
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawCentredString(x_pos + 10, y_pos + card_h - 13, number)
        pdf.setFillColor(INK)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(x_pos + 24, y_pos + card_h - 14, title)
        draw_wrapped_paragraph(pdf, body, SMALL_STYLE, x_pos + 24, y_pos + card_h - 20, card_w - 30)

    draw_card(
        pdf,
        18 * mm,
        28 * mm,
        82 * mm,
        46 * mm,
        "Why the lock exists",
        "The <b>DATA_LOCK</b> prevents two requests from writing the file at the same time. That reduces the chance of corrupted JSON when multiple actions happen close together.",
        SOFT_GREEN,
        "Thread safety",
    )
    draw_card(
        pdf,
        106 * mm,
        28 * mm,
        86 * mm,
        46 * mm,
        "How to host this app",
        "Install dependencies from <b>requirements.txt</b>, run the Flask app with a production server, and deploy it on a Python-friendly host such as Render, Railway, or PythonAnywhere.",
        SOFT_ORANGE,
        "Deployment",
    )


def page_four(pdf):
    setup_page(pdf, 4)
    x = 18 * mm
    y = PAGE_HEIGHT - 20 * mm
    draw_tag(pdf, x, y, "Beginner map", SOFT_GOLD)
    title_top = y - 14
    title_height = draw_wrapped_paragraph(
        pdf,
        "Which file should you open first?",
        TITLE_STYLE,
        x,
        title_top,
        150 * mm,
    )
    draw_wrapped_paragraph(
        pdf,
        "Use this reading order if you want to learn the code without feeling lost.",
        SUBTITLE_STYLE,
        x,
        title_top - title_height - 6,
        150 * mm,
    )

    roadmap = [
        ("Start with templates/index.html", "It shows the visible parts of the page, so it helps you connect code to what the user sees."),
        ("Then open static/app.js", "This is where the clicks and API calls happen. It answers 'how does the page react?'"),
        ("Then read app.py", "Now you can understand where the browser sends requests and how Python saves the tasks."),
        ("Read static/styles.css last", "CSS matters, but it is easier after you already know the structure and behavior."),
        ("Treat tasks.json as data", "This file is not logic. It is the saved result produced by the app."),
        ("Treat todo_list.py as an older prototype", "It is a command-line version created earlier, not the main web app used now."),
    ]

    current_y = PAGE_HEIGHT - 78 * mm
    for index, (title, body) in enumerate(roadmap, start=1):
        draw_round_rect(pdf, 22 * mm, current_y - 24 * mm, 166 * mm, 22 * mm, CARD)
        pdf.setFillColor(ACCENT)
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(28 * mm, current_y - 10 * mm, f"{index}. {title}")
        draw_wrapped_paragraph(pdf, body, SMALL_STYLE, 28 * mm, current_y - 13 * mm, 154 * mm)
        current_y -= 28 * mm

    draw_card(
        pdf,
        22 * mm,
        18 * mm,
        166 * mm,
        28 * mm,
        "Final takeaway",
        "A beginner can think of this app in three layers: screen, behavior, and storage. HTML/CSS create the screen, JavaScript drives behavior, and Python plus JSON handle storage.",
        SOFT_GOLD,
        "Memory hook",
    )


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    pdf = canvas.Canvas(str(OUTPUT_FILE), pagesize=A4)
    pdf.setTitle("To-Do App Code Infographic")
    pdf.setAuthor("OpenAI Codex")

    page_one(pdf)
    pdf.showPage()
    page_two(pdf)
    pdf.showPage()
    page_three(pdf)
    pdf.showPage()
    page_four(pdf)
    pdf.save()


if __name__ == "__main__":
    build_pdf()
    print(OUTPUT_FILE)
