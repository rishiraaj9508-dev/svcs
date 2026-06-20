from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table,
                                 TableStyle, PageBreak, HRFlowable)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY

W, H = A4
LM = RM = 14*mm
TM, BM = 22*mm, 18*mm
CW = W - LM - RM

# ── Palette ──────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#0A1628")
DBLUE   = colors.HexColor("#0D47A1")
BLUE    = colors.HexColor("#1565C0")
LBLUE   = colors.HexColor("#BBDEFB")
VBLUE   = colors.HexColor("#E3F2FD")
TEAL    = colors.HexColor("#00695C")
LTEAL   = colors.HexColor("#E0F7FA")
CYAN    = colors.HexColor("#006064")
LCYAN   = colors.HexColor("#E0F7FA")
GREEN   = colors.HexColor("#E8F5E9")
GREENT  = colors.HexColor("#1B5E20")
AMBER   = colors.HexColor("#FFF8E1")
AMBERT  = colors.HexColor("#E65100")
RED     = colors.HexColor("#B71C1C")
PINK    = colors.HexColor("#FCE4EC")
PURPLE  = colors.HexColor("#4A148C")
LPURPLE = colors.HexColor("#F3E5F5")
ORANGE  = colors.HexColor("#BF360C")
LORANGE = colors.HexColor("#FBE9E7")
CODE_BG = colors.HexColor("#F5F5F5")
CODE_BD = colors.HexColor("#BDBDBD")
GRAY    = colors.HexColor("#757575")
DGRAY   = colors.HexColor("#212121")
MGRAY   = colors.HexColor("#424242")
WHITE   = colors.white

def PS(name, **kw):
    d = dict(fontName='Helvetica', fontSize=10, leading=14,
             textColor=DGRAY, spaceBefore=2, spaceAfter=2)
    d.update(kw)
    return ParagraphStyle(name, **d)

UNIT_S = PS('UN', fontSize=22, fontName='Helvetica-Bold', textColor=WHITE,
            backColor=NAVY, alignment=TA_CENTER, spaceBefore=6, spaceAfter=4,
            leading=30, leftIndent=4, rightIndent=4)
SUB_S  = PS('SB', fontSize=9, textColor=GRAY, alignment=TA_CENTER,
            spaceBefore=0, spaceAfter=8)
H1_S   = PS('H1', fontSize=13, fontName='Helvetica-Bold', textColor=WHITE,
            backColor=DBLUE, spaceBefore=14, spaceAfter=4, leading=20, leftIndent=5)
H2_S   = PS('H2', fontSize=11, fontName='Helvetica-Bold', textColor=DBLUE,
            backColor=LBLUE, spaceBefore=9, spaceAfter=3, leading=17, leftIndent=5)
H3_S   = PS('H3', fontSize=10, fontName='Helvetica-Bold', textColor=BLUE,
            spaceBefore=7, spaceAfter=2, leading=15)
BODY_S = PS('BO', fontSize=9.5, textColor=MGRAY,
            spaceBefore=2, spaceAfter=3, leading=14, alignment=TA_JUSTIFY)
BULL_S = PS('BU', fontSize=9.5, textColor=MGRAY,
            spaceBefore=2, spaceAfter=2, leading=14, leftIndent=16, bulletIndent=4)
QS     = PS('QS', fontSize=9.5, fontName='Helvetica-Bold', textColor=AMBERT,
            spaceBefore=2, spaceAfter=2, leading=14)
AS     = PS('AS', fontSize=9.5, textColor=GREENT,
            spaceBefore=2, spaceAfter=2, leading=14)
ABS    = PS('AB', fontSize=9.5, textColor=GREENT,
            spaceBefore=1, spaceAfter=1, leading=14, leftIndent=14, bulletIndent=4)
NOTE_S = PS('NO', fontSize=9, fontName='Helvetica-Bold', textColor=RED,
            spaceBefore=2, spaceAfter=2, leading=13)
SM_S   = PS('SM', fontSize=7.5, textColor=GRAY, alignment=TA_CENTER)

def sp(n=5):  return Spacer(1, n)
def h1(t):    return [Paragraph(t, H1_S), sp(2)]
def h2(t):    return [Paragraph(t, H2_S), sp(2)]
def h3(t):    return [Paragraph(f"▶  {t}", H3_S), sp(1)]
def body(t):  return Paragraph(t, BODY_S)
def bull(t):  return Paragraph(f"•  {t}", BULL_S)
def note(t):  return Paragraph(f"★  {t}", NOTE_S)

def banner(text, sub=""):
    r = [Paragraph(text, UNIT_S)]
    if sub: r.append(Paragraph(sub, SUB_S))
    r.append(sp(6))
    return r

def ctable(headers, rows, widths=None):
    if not widths:
        w = CW/len(headers); widths = [w]*len(headers)
    hdr = [Paragraph(f"<b>{h}</b>", PS('TH', fontSize=9, fontName='Helvetica-Bold',
           textColor=WHITE, leading=13, alignment=TA_CENTER)) for h in headers]
    data = [hdr] + [[Paragraph(str(c), PS('TD', fontSize=9, textColor=MGRAY,
            leading=13)) for c in row] for row in rows]
    t = Table(data, colWidths=widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,0), DBLUE),
        ('ROWBACKGROUNDS', (0,1),(-1,-1), [WHITE, VBLUE]),
        ('GRID', (0,0),(-1,-1), 0.5, colors.HexColor("#90CAF9")),
        ('VALIGN', (0,0),(-1,-1), 'MIDDLE'),
        ('TOPPADDING',    (0,0),(-1,-1), 4),
        ('BOTTOMPADDING', (0,0),(-1,-1), 4),
        ('LEFTPADDING',   (0,0),(-1,-1), 5),
        ('RIGHTPADDING',  (0,0),(-1,-1), 5),
    ]))
    return [t, sp(6)]

def flow(steps, c1=34):
    rows = []
    for i,(lbl,desc) in enumerate(steps):
        bg = DBLUE if i%2==0 else BLUE
        rows.append([
            Table([[Paragraph(f"<b>{lbl}</b>", PS('FL', fontSize=9,
                   fontName='Helvetica-Bold', textColor=WHITE, leading=13,
                   alignment=TA_CENTER))]],colWidths=[c1*mm]),
            Paragraph(desc, PS('FD', fontSize=9, textColor=MGRAY, leading=13))])
    t = Table(rows, colWidths=[c1*mm, CW-c1*mm])
    ts = TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#90CAF9")),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)])
    for i in range(len(steps)):
        ts.add('BACKGROUND',(0,i),(0,i), DBLUE if i%2==0 else BLUE)
        ts.add('BACKGROUND',(1,i),(1,i), VBLUE if i%2==0 else WHITE)
    t.setStyle(ts)
    return [t, sp(6)]

def tip(label, text, bg=AMBER, tc=AMBERT):
    data = [[Paragraph(f"<b>{label}:</b>  {text}",
             PS('T', fontSize=9, textColor=tc, leading=13))]]
    t = Table(data, colWidths=[CW])
    t.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),0.6,tc),
        ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    return [t, sp(6)]

def diag(label, rows_data, colors_list=None):
    """Vertical flow diagram."""
    items = []
    n = len(rows_data)
    for i, (box, desc) in enumerate(rows_data):
        bg = colors_list[i] if colors_list else (DBLUE if i%2==0 else BLUE)
        row = Table([[
            Table([[Paragraph(f"<b>{box}</b>",
                    PS('DB', fontSize=9, fontName='Helvetica-Bold', textColor=WHITE,
                       leading=13, alignment=TA_CENTER))]],
                  colWidths=[38*mm]),
            Paragraph(desc, PS('DD', fontSize=9, textColor=MGRAY, leading=13))
        ]], colWidths=[38*mm, CW-38*mm])
        row.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(0,0),bg),
            ('BACKGROUND',(1,0),(1,0),VBLUE if i%2==0 else WHITE),
            ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#90CAF9")),
            ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
            ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),
            ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5)]))
        items.append(row)
        if i < n-1:
            arr = Table([[Paragraph("▼", PS('AR', fontSize=11, textColor=DBLUE,
                           alignment=TA_CENTER, spaceBefore=0, spaceAfter=0))]],
                        colWidths=[CW])
            arr.setStyle(TableStyle([('TOPPADDING',(0,0),(-1,-1),1),
                                     ('BOTTOMPADDING',(0,0),(-1,-1),1)]))
            items.append(arr)
    items.append(sp(6))
    return items

def qa(q, marks, items):
    qd = [[Paragraph(f"<b>Q.  {q}</b>   <font color='#B71C1C'>[{marks}]</font>", QS)]]
    qt = Table(qd, colWidths=[CW])
    qt.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),AMBER),
        ('BOX',(0,0),(-1,-1),0.8,colors.HexColor("#FFB300")),
        ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    arows = [[Paragraph(f"•  {t}" if b else t, ABS if b else AS)] for t,b in items]
    at = Table(arows, colWidths=[CW])
    at.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,-1),GREEN),
        ('BOX',(0,0),(-1,-1),0.8,colors.HexColor("#81C784")),
        ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
        ('LEFTPADDING',(0,0),(-1,-1),8)]))
    return [qt, at, sp(7)]

def on_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(LM, H-15*mm, CW, 9*mm, fill=1, stroke=0)
    canvas.setFont('Helvetica-Bold', 8.5)
    canvas.setFillColor(WHITE)
    canvas.drawString(LM+5, H-11*mm,
        "Artificial Intelligence  |  Unit 3 & Unit 4  |  Complete Exam Notes")
    canvas.setStrokeColor(DBLUE)
    canvas.setLineWidth(0.5)
    canvas.line(LM, 13*mm, W-RM, 13*mm)
    canvas.setFont('Helvetica', 7.5)
    canvas.setFillColor(GRAY)
    canvas.drawCentredString(W/2, 9*mm, f"Page {doc.page}")
    canvas.restoreState()

# ═══════════════════════════════════════════════════════════════════════
story = []

story += banner("Artificial Intelligence",
                "Unit 3 & Unit 4  —  Complete Exam Notes with Q&A")

# ═══════════════════════════════════════════════
# UNIT 3
# ═══════════════════════════════════════════════
story += h1("UNIT 3  —  Overview")
story.append(body(
    "Unit 3 covers four major topics: "
    "<b>(1) Game Playing</b> with Minimax Search and Alpha-Beta Pruning, "
    "<b>(2) Natural Language Processing (NLP)</b>, "
    "<b>(3) Learning</b> including Explanation-Based Learning, Discovery, and Analogy, and "
    "<b>(4) Neural Net Learning</b> and Genetic Algorithms."
))
story.append(sp(8))

# ────────────────────────────────────────────────
# TOPIC 1: GAME PLAYING
# ────────────────────────────────────────────────
story += h1("TOPIC 1 — Game Playing, Minimax Search & Alpha-Beta Cut-offs")

story += h2("1.1  Game Playing in AI")
story.append(body(
    "Game playing is one of the oldest and most studied areas of AI. "
    "Games like Chess, Checkers, and Tic-Tac-Toe provide a formal environment "
    "where AI agents must search for the best move. These are called "
    "<b>adversarial search problems</b> — two competing agents (MAX and MIN) take turns."
))
story.append(sp(3))
story += ctable(
    ["Property", "Description", "Example"],
    [["Deterministic", "Outcome is certain given moves", "Chess, Tic-Tac-Toe"],
     ["Stochastic", "Chance involved (dice, cards)", "Backgammon, Poker"],
     ["Perfect Info", "Both players see full board", "Chess, Go"],
     ["Imperfect Info", "Some info hidden", "Poker, Battleship"],
     ["Two-player Zero-sum", "One player's gain = other's loss", "Chess, Checkers"],],
    [32*mm, 72*mm, 70*mm])

story += h2("1.2  Minimax Search Algorithm")
story.append(body(
    "The <b>Minimax algorithm</b> is the foundation of game-playing AI. "
    "It explores the complete game tree and chooses the move that <b>maximizes</b> "
    "the score for MAX player, assuming MIN always plays <b>optimally</b> (minimizes score). "
    "It performs a <b>Depth-First Search (DFS)</b> of the game tree."
))
story.append(sp(3))

story += flow([
    ("Game Tree", "A tree where each node is a game state. Root = current position. Branches = possible moves."),
    ("MAX Player", "AI/Computer. At MAX nodes: choose the child with the HIGHEST value."),
    ("MIN Player", "Opponent. At MIN nodes: choose the child with the LOWEST value."),
    ("Terminal Node", "End of game. Assign utility value: +1 (win), 0 (draw), -1 (loss) for MAX."),
    ("Backed-up Value", "Propagate terminal values up the tree using max/min at each level."),
    ("Best Move", "At root (MAX), select the child with the highest backed-up value."),
])

story += h3("Minimax Algorithm (Pseudocode)")
story.append(body(
    "The algorithm recursively computes the best value for the current player at each node:"
))
story.append(sp(2))

pseudo_data = [
    ["MINIMAX(node, depth, isMaximizing):", ""],
    ["  IF terminal(node) OR depth == 0:", "Base case: leaf node or depth limit reached"],
    ["      RETURN evaluate(node)", "Return static evaluation of board"],
    ["  IF isMaximizing:", "MAX player's turn"],
    ["      best = -∞", "Start with worst possible value"],
    ["      FOR each child of node:", "Try every possible move"],
    ["          val = MINIMAX(child, depth-1, FALSE)", "Recurse for MIN player"],
    ["          best = MAX(best, val)", "Keep highest value"],
    ["      RETURN best", "Return best score for MAX"],
    ["  ELSE:  (MIN player)", "MIN player's turn"],
    ["      best = +∞", "Start with worst for MIN"],
    ["      FOR each child of node:", "Try every possible move"],
    ["          val = MINIMAX(child, depth-1, TRUE)", "Recurse for MAX player"],
    ["          best = MIN(best, val)", "Keep lowest value"],
    ["      RETURN best", "Return best score for MIN"],
]
code_rows = []
for line, comment in pseudo_data:
    safe_line = line.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace(' ','&nbsp;')
    safe_cmt  = comment.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
    row = [
        Paragraph(safe_line, PS('PL', fontSize=8.2, fontName='Courier',
                  textColor=DGRAY, leading=12, spaceBefore=0, spaceAfter=0)),
        Paragraph(safe_cmt,  PS('PC', fontSize=8.2, fontName='Helvetica',
                  textColor=GRAY,  leading=12, spaceBefore=0, spaceAfter=0)),
    ]
    code_rows.append(row)
ct = Table(code_rows, colWidths=[100*mm, CW-100*mm])
ct.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),CODE_BG),
    ('BOX',(0,0),(-1,-1),0.7,CODE_BD),
    ('TOPPADDING',(0,0),(-1,-1),2),('BOTTOMPADDING',(0,0),(-1,-1),2),
    ('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),5),
]))
story.append(ct)
story.append(sp(6))

story.append(body(
    "<b>Time Complexity:</b> O(b<sup>m</sup>) where b = branching factor, m = depth. "
    "<b>Space Complexity:</b> O(bm). "
    "For Chess: b≈35, m≈100 → completely impractical without pruning!"
))
story.append(sp(4))

story += h2("1.3  Alpha-Beta Pruning (Alpha-Beta Cut-offs)")
story.append(body(
    "Alpha-Beta Pruning is an <b>optimization of Minimax</b> that <b>prunes</b> (cuts off) "
    "branches that cannot possibly affect the final decision. It gives the <b>same result</b> "
    "as Minimax but explores <b>far fewer nodes</b>. Named after two values: <b>α (alpha)</b> "
    "and <b>β (beta)</b>."
))
story.append(sp(3))

story += ctable(
    ["Parameter", "Maintained by", "Meaning", "Pruning condition"],
    [["α (Alpha)", "MAX player", "Best value MAX can guarantee so far", "Prune at MIN node if α ≥ β"],
     ["β (Beta)",  "MIN player", "Best value MIN can guarantee so far", "Prune at MAX node if β ≤ α"],],
    [22*mm, 32*mm, 72*mm, 48*mm])

story.append(body(
    "<b>Alpha Cut-off:</b> At a MIN node, if a child value ≤ α (MAX's best), "
    "stop examining remaining children — MAX won't choose this path.<br/>"
    "<b>Beta Cut-off:</b> At a MAX node, if a child value ≥ β (MIN's best), "
    "stop examining remaining children — MIN won't allow this path."
))
story.append(sp(4))

story += flow([
    ("Best Case", "Nodes examined = O(b^(m/2)) — effectively doubles the search depth for same computation!"),
    ("Average Case", "O(b^(3m/4)) — significant improvement in practice"),
    ("Worst Case", "O(b^m) — same as minimax (when moves are ordered worst-first)"),
    ("Move Ordering", "Examining best moves first maximizes pruning. Good ordering crucial for efficiency."),
    ("Key Property", "Produces IDENTICAL result to full Minimax. No loss of accuracy — pure optimization."),
])

story += tip("Exam Mnemonic",
    "Alpha = MAX's lower bound (MAX wants HIGH). Beta = MIN's upper bound (MIN wants LOW). "
    "Prune when α ≥ β (window closes — no useful moves remain).")

story += h3("Alpha-Beta Pruning Worked Example")
story.append(body(
    "Given a game tree with values at leaves [3, 5, 2, 9, 0, 7, 4, 8] at depth 3 "
    "(branching factor 2):"
))
example_data = [
    ["Node", "Level", "α", "β", "Action"],
    ["Root", "MAX (0)", "-∞", "+∞", "Explore left subtree first"],
    ["Left child", "MIN (1)", "-∞", "+∞", "Explore, returns min(3,5)=3"],
    ["Root", "MAX (0)", "3", "+∞", "Update α=3, explore right"],
    ["Right child", "MIN (1)", "3", "+∞", "First leaf=2; β=2; 2 < α=3"],
    ["PRUNE", "—", "3", "2", "β ≤ α: prune remaining right subtree!"],
    ["Final", "MAX (0)", "3", "+∞", "Root selects value 3"],
]
et = Table(example_data, colWidths=[32*mm,28*mm,18*mm,18*mm,CW-96*mm])
et.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),DBLUE),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[WHITE,VBLUE]),
    ('GRID',(0,0),(-1,-1),0.5,colors.HexColor("#90CAF9")),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('BACKGROUND',(0,5),(-1,5),PINK),
    ('TEXTCOLOR',(0,5),(-1,5),RED),
    ('FONTNAME',(0,5),(-1,5),'Helvetica-Bold'),
    ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
]))
story.append(et)
story.append(sp(8))

# ────────────────────────────────────────────────
# TOPIC 2: NLP
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 2 — Natural Language Processing (NLP)")

story += h2("2.1  What is NLP?")
story.append(body(
    "<b>Natural Language Processing (NLP)</b> is a branch of AI that enables computers "
    "to understand, interpret, and generate <b>human language</b> (text and speech). "
    "It bridges the gap between human communication and computer understanding."
))
story.append(sp(3))
for b in [
    "Speech recognition (Siri, Alexa, Google Assistant)",
    "Machine translation (Google Translate)",
    "Sentiment analysis (product review rating)",
    "Chatbots and virtual assistants",
    "Information extraction (summarization, question answering)",
    "Spam detection in emails",
]:
    story.append(bull(b))
story.append(sp(4))

story += h2("2.2  NLP Pipeline — Levels of Analysis")
story += flow([
    ("Morphological", "Breaking words into roots and affixes. 'running' → 'run' + '-ing'. Deals with word structure."),
    ("Lexical", "Looking up word meanings in a dictionary/lexicon. 'Bank' = financial institution OR river bank."),
    ("Syntactic", "Parsing sentence grammar — subject, verb, object. Uses parse trees and grammar rules (CFG)."),
    ("Semantic", "Determining the meaning of words and sentences. Resolving ambiguity and word sense."),
    ("Pragmatic", "Understanding intent and context. Sarcasm, implied meaning, discourse context."),
    ("Discourse", "Analysing meaning across multiple sentences. Pronoun resolution, coherence, coreference."),
])

story += h2("2.3  Key NLP Tasks and Techniques")
story += ctable(
    ["Task", "Description", "Example"],
    [["Tokenization", "Split text into words/sentences", "'Hello World' → ['Hello','World']"],
     ["POS Tagging", "Label each word's grammar role", "'The cat sits' → DET NOUN VERB"],
     ["Parsing", "Build parse tree from grammar", "Subject-Verb-Object structure"],
     ["NER", "Named Entity Recognition — find names/places", "'Delhi is capital' → [Delhi=CITY]"],
     ["WSD", "Word Sense Disambiguation", "'bank': financial or river?"],
     ["IR", "Information Retrieval — search", "Google search engine"],
     ["MT", "Machine Translation", "English → Hindi"],
     ["Sentiment Analysis", "Detect positive/negative opinion", "'Great movie!' → Positive"],],
    [28*mm, 68*mm, 78*mm])

story += h2("2.4  Context-Free Grammar (CFG) in NLP")
story.append(body(
    "A <b>Context-Free Grammar (CFG)</b> defines the syntactic structure of language using rules. "
    "Each rule rewrites a non-terminal into terminals or other non-terminals."
))
story.append(sp(2))
cfg_rules = [
    ["Rule", "Meaning"],
    ["S → NP VP", "A Sentence = Noun Phrase + Verb Phrase"],
    ["NP → Det N", "Noun Phrase = Determiner + Noun"],
    ["VP → V NP", "Verb Phrase = Verb + Noun Phrase"],
    ["Det → 'the' | 'a'", "Determiner words"],
    ["N → 'cat' | 'dog' | 'mat'", "Nouns"],
    ["V → 'sat' | 'chased'", "Verbs"],
]
rt = Table(cfg_rules, colWidths=[60*mm, CW-60*mm])
rt.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),DBLUE),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[CODE_BG, WHITE]),
    ('GRID',(0,0),(-1,-1),0.5,CODE_BD),
    ('FONTNAME',(0,1),(-1,-1),'Courier'),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('LEFTPADDING',(0,0),(-1,-1),6),
]))
story.append(rt)
story.append(sp(4))
story.append(body(
    "<b>Parse Tree Example:</b> 'The cat sat on the mat' → "
    "S[NP[Det[the] N[cat]] VP[V[sat] PP[P[on] NP[Det[the] N[mat]]]]]"
))
story.append(sp(3))
story += tip("Ambiguity in NLP",
    "Ambiguity is the biggest challenge. 'I saw the man with the telescope' — "
    "did I use the telescope, or did the man have it? Syntactic ambiguity. "
    "NLP resolves this using probability and context.")

# ────────────────────────────────────────────────
# TOPIC 3: LEARNING
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 3 — Learning, Explanation-Based Learning, Discovery & Analogy")

story += h2("3.1  What is Machine Learning in AI?")
story.append(body(
    "<b>Learning</b> in AI means a system improves its performance on tasks through experience, "
    "without being explicitly programmed for every situation. "
    "It is the ability to generalise from examples."
))
story.append(sp(3))
story += ctable(
    ["Type of Learning", "Description", "Example"],
    [["Supervised", "Learn from labelled (input,output) pairs", "Spam classifier"],
     ["Unsupervised", "Find patterns in unlabelled data", "Customer clustering"],
     ["Reinforcement", "Learn from rewards/penalties", "Game-playing AI"],
     ["Explanation-Based", "Learn from a single example using domain knowledge", "Learn 'cup' from one example"],
     ["Analogy-Based", "Learn by mapping known domain to new domain", "Solar system → atom model"],
     ["Discovery", "Find new concepts by exploring data without guidance", "Scientific hypothesis generation"],],
    [36*mm, 78*mm, 60*mm])

story += h2("3.2  Explanation-Based Learning (EBL)")
story.append(body(
    "<b>Explanation-Based Learning (EBL)</b> is a form of learning where the system learns a general "
    "concept from a <b>single training example</b> by using <b>background domain knowledge</b> to "
    "construct an explanation of why the example is an instance of the concept, then generalises "
    "from that explanation."
))
story.append(sp(3))

story += flow([
    ("Step 1: Training Example", "A single labelled example is provided. E.g., a specific cup with handle, holds liquid, stable."),
    ("Step 2: Goal Concept", "The concept to be learned. E.g., 'CUP = something that can be used for drinking'."),
    ("Step 3: Domain Theory", "Background rules/knowledge already available. E.g., 'Anything stable + holds liquid + liftable = cup'."),
    ("Step 4: Explanation", "Use domain theory to construct why the example IS an instance of the goal concept."),
    ("Step 5: Generalise", "Replace specific constants with variables to create a general rule."),
    ("Step 6: Result", "A new general rule that can classify future examples without retraining."),
])

story.append(sp(3))
story += h3("EBL Example — Learning 'Safe to Stack'")
story.append(body(
    "<b>Training Example:</b> Block A (color=Red, size=Small, weight=Light) is safe to stack on Block B (size=Large).<br/>"
    "<b>Domain Theory:</b> 'Can_support(X,Y) if weight(Y, Light)'. 'Safe_to_stack(Y,X) if Can_support(X,Y)'.<br/>"
    "<b>Explanation:</b> Weight(A,Light) → Can_support(B,A) → Safe_to_stack(A,B).<br/>"
    "<b>Generalised Rule:</b> Safe_to_stack(Y,X) ← weight(Y, Light). "
    "(Works for ANY light block, not just block A!)"
))
story.append(sp(3))

story += ctable(
    ["Aspect", "EBL", "Traditional Inductive Learning"],
    [["Examples needed", "ONE example sufficient", "Many examples required"],
     ["Background knowledge", "Rich domain theory required", "Not required"],
     ["Generalisation", "From explanation structure", "From statistical patterns"],
     ["Speed", "Fast (single example)", "Slow (many examples)"],
     ["Risk", "Depends on quality of domain theory", "Depends on data quality"],],
    [40*mm, 70*mm, 64*mm])

story += h2("3.3  Learning by Discovery")
story.append(body(
    "<b>Learning by Discovery</b> is the autonomous generation of new knowledge by exploring "
    "the problem space without explicit supervision. The AI discovers new concepts, "
    "patterns, or laws from raw data or simulated experiments."
))
story.append(sp(2))
for b in [
    "Scientific discovery systems: AM (Automated Mathematician) discovered properties of prime numbers",
    "BACON system: rediscovered Kepler's laws and Ohm's law from experimental data",
    "The system generates hypotheses, tests them, and retains those that explain observations",
    "Key steps: Observe → Form hypothesis → Test hypothesis → Generalise → Refine",
    "Used in drug discovery, material science, astronomical pattern detection",
]:
    story.append(bull(b))
story.append(sp(4))

story += h2("3.4  Learning by Analogy")
story.append(body(
    "<b>Analogical reasoning</b> means solving a new problem by mapping it to a structurally "
    "similar, previously solved problem. The solution is then <b>transferred</b> from the "
    "source domain to the target domain."
))
story.append(sp(2))
story += flow([
    ("Source Domain", "Well-understood domain. E.g., Solar system: Sun at center, planets orbit it."),
    ("Target Domain", "New domain to understand. E.g., Atom: nucleus at center, electrons orbit."),
    ("Structural Mapping", "Find correspondences: Sun↔Nucleus, Planet↔Electron, Orbit↔Orbit."),
    ("Transfer", "Apply source knowledge to target: 'Electrons orbit nucleus like planets orbit sun'."),
    ("Validate", "Test if the analogy holds. Refine where it breaks down."),
])
story.append(sp(2))
story.append(body(
    "<b>Examples of Analogical Reasoning:</b> "
    "Water flow analogy for electricity (voltage=pressure, current=flow, resistance=pipe width). "
    "Human memory analogised to computer RAM. "
    "Designing a bridge by analogy to a strong tree structure."
))
story.append(sp(4))

story += tip("EBL vs Discovery vs Analogy",
    "EBL: Uses 1 example + domain knowledge → deep explanation. "
    "Discovery: No examples, explores freely → finds patterns. "
    "Analogy: Maps familiar solved domain → new problem domain.")

# ────────────────────────────────────────────────
# TOPIC 4: NEURAL NET & GENETIC
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 4 — Neural Net Learning & Genetic Learning")

story += h2("4.1  Biological Inspiration")
story.append(body(
    "Neural networks are inspired by the human brain. The brain contains ~86 billion neurons, "
    "each connected to thousands of others. Information is processed by weighted connections. "
    "Artificial Neural Networks (ANNs) mimic this with mathematical models."
))
story.append(sp(4))

story += h2("4.2  Artificial Neuron (Perceptron)")
story.append(body(
    "The <b>Perceptron</b> is the simplest artificial neuron. It takes multiple weighted inputs, "
    "sums them, adds a bias, and passes through an activation function to produce output."
))
story.append(sp(3))
story += flow([
    ("Inputs (x₁,x₂,...,xₙ)", "Feature values fed to the neuron. E.g., pixel values, sensor readings."),
    ("Weights (w₁,w₂,...,wₙ)", "Learnable parameters. Determine importance of each input."),
    ("Bias (b)", "Extra parameter allowing the activation threshold to shift."),
    ("Weighted Sum", "z = w₁x₁ + w₂x₂ + ... + wₙxₙ + b  = Σ(wᵢxᵢ) + b"),
    ("Activation f(z)", "Non-linear function applied to z. Determines output range and behaviour."),
    ("Output ŷ", "Final output of the neuron. Used for prediction or passed to next layer."),
])

story += h3("Common Activation Functions")
story += ctable(
    ["Function", "Formula", "Output Range", "Use Case"],
    [["Step", "1 if z≥0, else 0", "{0, 1}", "Binary perceptron (classic)"],
     ["Sigmoid", "1/(1+e^(-z))", "(0, 1)", "Binary classification output"],
     ["Tanh", "(e^z-e^(-z))/(e^z+e^(-z))", "(-1, 1)", "Hidden layers (zero-centred)"],
     ["ReLU", "max(0, z)", "[0, ∞)", "Hidden layers (modern default)"],
     ["Softmax", "e^zᵢ/Σe^zⱼ", "(0,1) sums to 1", "Multi-class output layer"],],
    [22*mm, 48*mm, 28*mm, 76*mm])

story += h2("4.3  Multilayer Feedforward Network (MLP)")
story.append(body(
    "A <b>Multilayer Perceptron (MLP)</b> consists of: "
    "an <b>Input Layer</b> (receives features), "
    "one or more <b>Hidden Layers</b> (learn representations), "
    "and an <b>Output Layer</b> (produces predictions). "
    "All connections go forward (no cycles) — hence <b>feedforward</b>."
))
story.append(sp(4))

# Architecture visual
arch_data = [
    ("Input Layer\n(x₁, x₂, ..., xₙ)", "Receives raw feature values. One neuron per feature. No computation — just passes data forward."),
    ("Hidden Layer 1", "Learns low-level patterns. Each neuron = weighted sum + activation. Weights learned by backprop."),
    ("Hidden Layer 2\n(optional)", "Learns higher-level abstractions. More hidden layers = deeper network = more capacity."),
    ("Output Layer\n(ŷ₁, ..., ŷₖ)", "One neuron per class (classification) or one neuron (regression). Applies softmax/sigmoid."),
]
for box, desc in arch_data:
    story += diag("", [(box, desc)])

story.append(sp(4))

story += h2("4.4  Backpropagation — How Neural Networks Learn")
story.append(body(
    "<b>Backpropagation</b> (backward propagation of errors) is the algorithm used to train "
    "neural networks. It calculates how much each weight contributed to the error and "
    "adjusts weights using <b>gradient descent</b>."
))
story.append(sp(3))
story += flow([
    ("1. Forward Pass", "Feed input through network layer by layer. Compute predicted output ŷ."),
    ("2. Compute Loss", "Compare ŷ with true label y using loss function. E.g., MSE = (y-ŷ)², Cross-Entropy."),
    ("3. Backward Pass", "Use chain rule to compute ∂Loss/∂w for every weight w. Propagate error backward."),
    ("4. Update Weights", "w ← w - η · (∂Loss/∂w). η = learning rate (step size)."),
    ("5. Repeat", "Repeat for all training examples (one epoch). Run multiple epochs until convergence."),
])
story.append(sp(3))
story.append(body(
    "<b>Key Concepts:</b><br/>"
    "• <b>Learning Rate (η):</b> Too high = overshoot minimum. Too low = very slow convergence.<br/>"
    "• <b>Epoch:</b> One full pass through all training data.<br/>"
    "• <b>Batch Gradient Descent:</b> Update weights after entire dataset.<br/>"
    "• <b>Mini-Batch SGD:</b> Update after small batches (most common in practice).<br/>"
    "• <b>Overfitting:</b> Network memorises training data but fails on new data. Fixed by dropout, regularisation."
))
story.append(sp(4))

story += h2("4.5  Genetic Algorithms (GA)")
story.append(body(
    "<b>Genetic Algorithms</b> are search/optimisation algorithms inspired by "
    "<b>Darwinian evolution</b>. They maintain a <b>population</b> of candidate solutions "
    "and evolve them over generations using genetic operators until the best solution emerges."
))
story.append(sp(3))

story += flow([
    ("1. Initialise", "Create initial population of N random individuals (chromosomes = candidate solutions)."),
    ("2. Evaluate Fitness", "Compute fitness score for each individual using a fitness function."),
    ("3. Selection", "Select parents based on fitness. Fitter individuals more likely to be selected."),
    ("4. Crossover", "Combine two parents to create offspring. One-point, two-point, or uniform crossover."),
    ("5. Mutation", "Randomly flip bits in offspring with small probability. Maintains diversity."),
    ("6. Replace", "New generation replaces old population (elitism: keep best individual always)."),
    ("7. Repeat", "Repeat steps 2–6 until convergence or max generations reached."),
])

story += h3("GA Terminology")
story += ctable(
    ["Term", "Meaning", "Example (Route Planning)"],
    [["Chromosome", "One candidate solution", "One possible route: [A→C→B→D]"],
     ["Gene", "One component of solution", "A city in the route"],
     ["Population", "Set of all current solutions", "100 different routes"],
     ["Fitness Function", "Measures quality of solution", "Total distance (minimise)"],
     ["Crossover", "Combine two parent solutions", "Merge two routes at midpoint"],
     ["Mutation", "Random small change", "Swap two cities in route"],
     ["Generation", "One iteration of the algorithm", "Population after one round of GA"],
     ["Elitism", "Keep the best individual always", "Best route always survives"],],
    [34*mm, 60*mm, 80*mm])

story += h3("GA Example — Optimising Binary String (Maximise number of 1s)")
story.append(body(
    "<b>Problem:</b> Find an 8-bit binary string with maximum 1s (answer: 11111111).<br/>"
    "<b>Encoding:</b> Each individual = 8-bit string. Fitness = count of 1s.<br/>"
    "<b>Initial population:</b> [01001011]=4, [11010001]=4, [10101010]=4, [01110011]=5<br/>"
    "<b>Select best two:</b> [01110011] and [11010001] → Cross at bit 4:<br/>"
    "<b>Offspring:</b> [0111|0001] and [1101|0011]. Mutate bit 5 of child1: [01111001]=6.<br/>"
    "<b>After several generations:</b> Population converges towards [11111111]=8."
))
story.append(sp(4))

story += ctable(
    ["Feature", "Neural Networks", "Genetic Algorithms"],
    [["Inspiration", "Brain neurons", "Biological evolution"],
     ["Learning mechanism", "Gradient descent + backprop", "Selection, crossover, mutation"],
     ["Representation", "Weights and activations", "Population of chromosomes"],
     ["Best for", "Pattern recognition, classification", "Optimisation, search problems"],
     ["Requires", "Differentiable objective", "Only fitness evaluation"],
     ["Examples", "Image/speech recognition", "TSP, scheduling, parameter tuning"],],
    [38*mm, 64*mm, 72*mm])

# ═══════════════════════════════════════════════
# UNIT 4
# ═══════════════════════════════════════════════
story.append(PageBreak())
story += h1("UNIT 4  —  Overview")
story.append(body(
    "Unit 4 covers four major topics: "
    "<b>(1) Fuzzy Logic Systems</b> and Perception & Action, "
    "<b>(2) Expert Systems</b> and Inference in Bayesian Networks, "
    "<b>(3) K-Means Clustering Algorithm</b>, and "
    "<b>(4) Machine Learning</b> concepts and methods."
))
story.append(sp(8))

# ────────────────────────────────────────────────
# TOPIC 5: FUZZY LOGIC
# ────────────────────────────────────────────────
story += h1("TOPIC 5 — Fuzzy Logic Systems, Perception and Action")

story += h2("5.1  Classical Logic vs Fuzzy Logic")
story.append(body(
    "<b>Classical (Crisp) Logic:</b> Everything is either TRUE (1) or FALSE (0). "
    "A person is either 'tall' or 'not tall'. No middle ground.<br/><br/>"
    "<b>Fuzzy Logic:</b> Introduced by Lotfi Zadeh (1965). Allows <b>degrees of truth</b> "
    "between 0 and 1. A person can be 'quite tall' (0.7) or 'somewhat tall' (0.4). "
    "Models the vagueness of human thinking."
))
story.append(sp(3))
story += ctable(
    ["Aspect", "Classical (Crisp) Logic", "Fuzzy Logic"],
    [["Truth Values", "0 or 1 only", "Any value in [0, 1]"],
     ["Sets", "Crisp sets: in or out", "Fuzzy sets: partial membership"],
     ["Temperature", "'Hot' or 'Not Hot'", "'Hot' = 0.8, 'Warm' = 0.4"],
     ["Human reasoning", "Poor match", "Good match"],
     ["Application", "Digital circuits", "Control systems, AI"],],
    [34*mm, 70*mm, 70*mm])

story += h2("5.2  Fuzzy Sets and Membership Functions")
story.append(body(
    "A <b>Fuzzy Set</b> assigns a <b>membership degree μ(x) ∈ [0,1]</b> to each element. "
    "The <b>membership function</b> defines how each element maps to its membership degree. "
    "Common shapes: triangular, trapezoidal, Gaussian."
))
story.append(sp(3))
story.append(body(
    "<b>Example — Temperature (°C):</b><br/>"
    "• COLD: μ(0°C)=1.0, μ(10°C)=0.5, μ(20°C)=0.0<br/>"
    "• WARM: μ(15°C)=0.3, μ(25°C)=1.0, μ(35°C)=0.3<br/>"
    "• HOT:  μ(30°C)=0.0, μ(40°C)=0.5, μ(50°C)=1.0"
))
story.append(sp(3))

story += h3("Fuzzy Set Operations")
story += ctable(
    ["Operation", "Formula", "Meaning"],
    [["AND (Intersection)", "μ(A∩B) = min(μA, μB)", "Smallest membership"],
     ["OR  (Union)",        "μ(A∪B) = max(μA, μB)", "Largest membership"],
     ["NOT (Complement)",   "μ(Ā)   = 1 − μA",       "Invert membership"],],
    [44*mm, 56*mm, 74*mm])

story += h2("5.3  Fuzzy Inference System (FIS)")
story += flow([
    ("1. Fuzzification", "Convert crisp input values into fuzzy membership values. 25°C → HOT=0.2, WARM=0.8"),
    ("2. Rule Evaluation", "Apply fuzzy IF-THEN rules. E.g., IF temp IS HOT THEN fan_speed IS FAST"),
    ("3. Aggregation", "Combine outputs of all rules (using max or sum)."),
    ("4. Defuzzification", "Convert fuzzy output back to a crisp value. Centroid method: x* = Σ(x·μ)/Σμ"),
])

story.append(sp(2))
story.append(body(
    "<b>Example — Air Conditioner Fuzzy Rules:</b><br/>"
    "R1: IF temperature IS Cold THEN cooling IS Slow<br/>"
    "R2: IF temperature IS Warm THEN cooling IS Medium<br/>"
    "R3: IF temperature IS Hot  THEN cooling IS Fast<br/>"
    "For input 35°C: μ(Hot)=0.7, μ(Warm)=0.3 → Aggregated output → Defuzzify → Fan speed = 78%"
))
story.append(sp(3))

story += h2("5.4  Perception and Action in AI")
story.append(body(
    "An AI agent perceives its environment through sensors and acts through actuators. "
    "The <b>Perception-Action cycle</b> is fundamental to intelligent agents (robots, self-driving cars)."
))
story.append(sp(3))
story += flow([
    ("Perception", "Sensors collect raw data: cameras (vision), microphones (sound), GPS, accelerometers."),
    ("Interpretation", "Process raw data: edge detection, object recognition, speech recognition."),
    ("Reasoning", "Decide what action to take based on current percepts and goals."),
    ("Action", "Execute decision via actuators: motors, speakers, displays, robotic arms."),
    ("Feedback", "Observe result of action and update internal model of the environment."),
])
story += tip("Fuzzy Logic Applications",
    "Traffic light control, washing machine load sensing, anti-lock braking systems (ABS), "
    "stock trading systems, medical diagnosis, camera autofocus.")

# ────────────────────────────────────────────────
# TOPIC 6: EXPERT SYSTEMS & BAYESIAN NETWORKS
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 6 — Expert Systems & Inference in Bayesian Networks")

story += h2("6.1  Expert Systems")
story.append(body(
    "An <b>Expert System</b> is an AI program that mimics the decision-making ability of a "
    "human expert in a specific domain. It uses a <b>knowledge base</b> of expert rules and "
    "an <b>inference engine</b> to draw conclusions."
))
story.append(sp(3))

story += flow([
    ("Knowledge Base", "Stores domain-specific facts and IF-THEN rules. Built by a knowledge engineer."),
    ("Inference Engine", "Applies rules to facts to derive new conclusions. Uses forward or backward chaining."),
    ("Working Memory", "Holds current facts and intermediate conclusions during a session."),
    ("Explanation Facility", "Explains HOW and WHY a conclusion was reached."),
    ("User Interface", "Allows non-experts to interact and query the system."),
    ("Knowledge Acquisition", "Interface for experts to add/update rules."),
])

story += h3("Forward Chaining vs Backward Chaining")
story += ctable(
    ["Aspect", "Forward Chaining (Data-Driven)", "Backward Chaining (Goal-Driven)"],
    [["Direction", "Facts → Rules → Conclusion", "Goal → Rules → Facts needed"],
     ["Starts with", "Known facts", "Hypothesis/goal"],
     ["Explores", "All possible conclusions", "Only paths leading to goal"],
     ["Best for", "Monitoring, planning", "Diagnosis, debugging"],
     ["Example", "Given symptoms → diagnose", "Prove 'patient has flu' → find evidence"],],
    [28*mm, 78*mm, 68*mm])

story.append(sp(4))
story += h3("Expert System Example — Medical Diagnosis")
rules_data = [
    ["Rule", "IF (condition)", "THEN (conclusion)"],
    ["R1", "fever=high AND cough=yes", "suspect = flu"],
    ["R2", "suspect=flu AND fatigue=yes", "diagnosis = influenza"],
    ["R3", "fever=high AND rash=yes", "suspect = dengue"],
    ["R4", "suspect=dengue AND headache=yes", "diagnosis = dengue_fever"],
]
rt = Table(rules_data, colWidths=[20*mm, 90*mm, CW-110*mm])
rt.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),DBLUE),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[CODE_BG,WHITE]),
    ('GRID',(0,0),(-1,-1),0.5,CODE_BD),
    ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),
    ('LEFTPADDING',(0,0),(-1,-1),5),
]))
story.append(rt)
story.append(sp(4))
story.append(body(
    "<b>Given facts:</b> fever=high, cough=yes, fatigue=yes<br/>"
    "<b>Forward Chaining:</b> R1 fires → suspect=flu. R2 fires → <b>diagnosis = influenza</b>."
))
story.append(sp(4))

story += h2("6.2  Bayesian Networks (Belief Networks)")
story.append(body(
    "A <b>Bayesian Network</b> is a probabilistic graphical model that represents a set of "
    "variables and their conditional dependencies via a <b>Directed Acyclic Graph (DAG)</b>. "
    "Nodes = random variables. Edges = direct probabilistic dependencies. "
    "Each node has a <b>Conditional Probability Table (CPT)</b>."
))
story.append(sp(3))

story += flow([
    ("Node", "Represents a random variable. E.g., Rain, Sprinkler, WetGrass."),
    ("Directed Edge", "A→B means A directly influences B. E.g., Rain → WetGrass."),
    ("CPT", "Conditional Probability Table: P(node | parents). E.g., P(WetGrass | Rain, Sprinkler)."),
    ("Joint Probability", "P(X₁,...,Xₙ) = ∏ P(Xᵢ | parents(Xᵢ))"),
    ("Inference", "Query: Given some observed variables (evidence), compute probability of others."),
])

story.append(sp(3))
story += h3("Bayesian Network Example — Wet Grass")
story.append(body(
    "<b>Variables:</b> Cloudy (C), Rain (R), Sprinkler (S), WetGrass (W)<br/>"
    "<b>Structure:</b> Cloudy → Rain, Cloudy → Sprinkler, Rain → WetGrass, Sprinkler → WetGrass<br/>"
    "<b>CPTs (example values):</b>"
))
story.append(sp(2))
cpt_data = [
    ["P(Cloudy)", "P(Rain|Cloudy)", "P(Sprinkler|Cloudy)", "P(WetGrass|Rain,Sprinkler)"],
    ["P(C=T)=0.5", "P(R=T|C=T)=0.8", "P(S=T|C=T)=0.1", "P(W=T|R=T,S=T)=0.99"],
    ["P(C=F)=0.5", "P(R=T|C=F)=0.2", "P(S=T|C=F)=0.5", "P(W=T|R=T,S=F)=0.90"],
    ["", "", "", "P(W=T|R=F,S=T)=0.90"],
    ["", "", "", "P(W=T|R=F,S=F)=0.01"],
]
cptt = Table(cpt_data, colWidths=[CW/4]*4)
cptt.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,0),DBLUE),('TEXTCOLOR',(0,0),(-1,0),WHITE),
    ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ('ROWBACKGROUNDS',(0,1),(-1,-1),[CODE_BG,WHITE,CODE_BG,WHITE]),
    ('GRID',(0,0),(-1,-1),0.5,CODE_BD),
    ('FONTSIZE',(0,0),(-1,-1),8.5),
    ('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),
    ('LEFTPADDING',(0,0),(-1,-1),4),
]))
story.append(cptt)
story.append(sp(4))
story.append(body(
    "<b>Inference Query:</b> P(Rain=T | WetGrass=T) = ?<br/>"
    "Use Bayes' theorem: P(R|W) = P(W|R)·P(R) / P(W)<br/>"
    "<b>Calculation:</b> Marginalise over Cloudy and Sprinkler to get P(Rain=T|WetGrass=T) ≈ 0.708"
))
story.append(sp(3))
story += tip("Bayesian Networks Use Cases",
    "Medical diagnosis, spam filtering, fault detection in industrial systems, "
    "speech recognition, gene expression analysis, risk assessment.")

# ────────────────────────────────────────────────
# TOPIC 7: K-MEANS
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 7 — K-Means Clustering Algorithm")

story += h2("7.1  What is Clustering?")
story.append(body(
    "<b>Clustering</b> is an <b>unsupervised learning</b> task where the goal is to group "
    "similar data points together without any pre-defined labels. "
    "<b>K-Means</b> is the most popular and simple clustering algorithm."
))
story.append(sp(3))
story += ctable(
    ["Type", "Description"],
    [["K-Means", "Partition-based. Assigns each point to nearest centroid."],
     ["Hierarchical", "Builds a tree (dendrogram) of clusters."],
     ["DBSCAN", "Density-based. Finds arbitrarily shaped clusters."],
     ["GMM", "Gaussian Mixture Models — probabilistic soft clustering."],],
    [40*mm, CW-40*mm])

story += h2("7.2  K-Means Algorithm — Step by Step")
story.append(body(
    "<b>Goal:</b> Partition N data points into <b>K clusters</b> by minimising the "
    "<b>Within-Cluster Sum of Squares (WCSS)</b> = Σ Σ ||xᵢ - μₖ||²"
))
story.append(sp(3))
story += flow([
    ("Step 1: Choose K", "Select number of clusters K (hyperparameter chosen by user)."),
    ("Step 2: Initialise", "Randomly choose K data points as initial centroids μ₁, μ₂, ..., μₖ."),
    ("Step 3: Assign", "For EACH data point, compute distance to EACH centroid. Assign to nearest centroid's cluster."),
    ("Step 4: Update", "Recompute centroid of each cluster = mean of all points assigned to it. μₖ = (1/|Cₖ|) Σxᵢ"),
    ("Step 5: Check", "If centroids changed: go back to Step 3. If centroids did not change: STOP (converged)."),
    ("Result", "K clusters where each point belongs to the cluster with the nearest centroid."),
])

story.append(sp(4))
story += h3("K-Means Numerical Example")
story.append(body(
    "<b>Data points (2D):</b> A(1,1), B(1,2), C(2,1), D(8,8), E(9,8), F(8,9). K=2<br/><br/>"
    "<b>Iteration 1:</b><br/>"
    "Initial centroids: C1=(1,1), C2=(8,8)<br/>"
    "Assign: A→C1, B→C1, C→C1 (close to (1,1)); D→C2, E→C2, F→C2 (close to (8,8))<br/>"
    "Update: C1 = mean((1,1),(1,2),(2,1)) = (4/3, 4/3) ≈ (1.33, 1.33)<br/>"
    "Update: C2 = mean((8,8),(9,8),(8,9)) = (25/3, 25/3) ≈ (8.33, 8.33)<br/><br/>"
    "<b>Iteration 2:</b><br/>"
    "Reassign with new centroids — same assignment as before.<br/>"
    "Centroids unchanged → <b>CONVERGED!</b><br/>"
    "Final clusters: Cluster1={A,B,C}, Cluster2={D,E,F}"
))
story.append(sp(4))

story += h2("7.3  Choosing K — The Elbow Method")
story.append(body(
    "Run K-Means for K=1,2,3,...,n. Plot <b>WCSS vs K</b>. "
    "The curve drops steeply then levels off. The 'elbow point' (where the curve bends) "
    "is the optimal K. Beyond that point, adding more clusters gives diminishing returns."
))
story.append(sp(3))

story += h2("7.4  K-Means: Advantages, Limitations, Applications")
story += ctable(
    ["Advantages", "Limitations"],
    [["Simple and easy to implement", "Must specify K in advance"],
     ["Scales well to large datasets", "Sensitive to initial centroid placement"],
     ["Guaranteed to converge", "Assumes spherical, equal-sized clusters"],
     ["Efficient: O(n·K·d·i) time", "Sensitive to outliers and noise"],
     ["Works well when clusters are well-separated", "Finds local minimum, not global minimum"],],
    [CW//2, CW//2])
story.append(sp(3))
story.append(body(
    "<b>Applications:</b> Customer segmentation, image compression (colour quantisation), "
    "document clustering, anomaly detection, gene expression analysis, city planning."
))
story.append(sp(4))

# ────────────────────────────────────────────────
# TOPIC 8: MACHINE LEARNING
# ────────────────────────────────────────────────
story.append(PageBreak())
story += h1("TOPIC 8 — Machine Learning")

story += h2("8.1  Definition of Machine Learning")
story.append(body(
    "<b>Machine Learning (ML)</b> is a subset of AI where systems learn from data "
    "and improve their performance on tasks <b>without being explicitly programmed</b>. "
    "Coined by Arthur Samuel (1959). Formalised by Tom Mitchell: "
    "<i>'A computer program learns from experience E with respect to task T and "
    "performance measure P, if its performance on T improves with experience E.'</i>"
))
story.append(sp(4))

story += h2("8.2  Types of Machine Learning")
story += flow([
    ("Supervised Learning", "Labelled training data (X, Y). Learn mapping X→Y. Train on examples, predict on new data."),
    ("Unsupervised Learning", "Unlabelled data (X only). Find hidden structure: clusters, density, associations."),
    ("Semi-Supervised", "Mix of labelled and unlabelled data. Label propagation."),
    ("Reinforcement Learning", "Agent learns by interacting with environment. Maximise cumulative reward."),
    ("Self-Supervised", "Labels generated from data itself. E.g., predict masked words (BERT)."),
])

story += h2("8.3  Supervised Learning — Key Algorithms")
story += ctable(
    ["Algorithm", "Type", "How it works", "Use Case"],
    [["Linear Regression", "Regression", "Fit best line y=mx+b minimising squared error", "House price prediction"],
     ["Logistic Regression", "Classification", "Sigmoid output → probability of class", "Spam detection"],
     ["Decision Tree", "Both", "Split data on features maximising information gain", "Medical diagnosis"],
     ["Random Forest", "Both", "Ensemble of many decision trees (bagging)", "Credit risk scoring"],
     ["SVM", "Classification", "Find hyperplane maximising margin between classes", "Image classification"],
     ["K-NN", "Both", "Classify by majority vote of K nearest training points", "Recommendation systems"],
     ["Naive Bayes", "Classification", "Apply Bayes theorem with independence assumption", "Text classification"],
     ["Neural Network", "Both", "Layers of neurons learn non-linear patterns", "Image/speech recognition"],],
    [36*mm, 24*mm, 76*mm, 38*mm])

story += h2("8.4  The ML Workflow")
story += flow([
    ("1. Problem Definition", "Define task: classification, regression, clustering? Define success metric."),
    ("2. Data Collection", "Gather relevant data from databases, APIs, sensors, web scraping."),
    ("3. Data Preprocessing", "Handle missing values, remove outliers, normalise features, encode categories."),
    ("4. Feature Engineering", "Select/create relevant features. PCA for dimensionality reduction."),
    ("5. Model Selection", "Choose algorithm(s). Split data: 70% train, 15% validation, 15% test."),
    ("6. Training", "Fit model on training data. Tune hyperparameters using validation set."),
    ("7. Evaluation", "Measure on test set: Accuracy, Precision, Recall, F1, AUC-ROC, RMSE."),
    ("8. Deployment", "Integrate model into application. Monitor performance over time."),
])

story += h2("8.5  Overfitting vs Underfitting")
story += ctable(
    ["Problem", "Description", "Symptoms", "Solution"],
    [["Underfitting", "Model too simple", "High train error + high test error", "More features, complex model, less regularisation"],
     ["Good Fit", "Model just right", "Low train error + low test error", "Keep this!"],
     ["Overfitting", "Model memorises training data", "Low train error + HIGH test error", "More data, dropout, regularisation (L1/L2), cross-validation"],],
    [28*mm, 42*mm, 56*mm, 48*mm])

story += h2("8.6  Evaluation Metrics")
story += ctable(
    ["Metric", "Formula", "Use When"],
    [["Accuracy", "(TP+TN)/(TP+TN+FP+FN)", "Balanced classes"],
     ["Precision", "TP/(TP+FP)", "Minimise false positives (spam filter)"],
     ["Recall", "TP/(TP+FN)", "Minimise false negatives (cancer screening)"],
     ["F1 Score", "2·(P·R)/(P+R)", "Imbalanced classes"],
     ["MSE/RMSE", "Σ(y-ŷ)²/n  or  √MSE", "Regression tasks"],
     ["AUC-ROC", "Area under ROC curve", "Binary classification"],],
    [28*mm, 56*mm, 90*mm])

story += tip("ML Key Terms",
    "Hyperparameter = set before training (K in K-NN, learning rate). "
    "Parameter = learned during training (weights). "
    "Cross-validation = train/evaluate on multiple splits to get reliable estimate.")

# ═══════════════════════════════════════════════
# Q & A SECTION
# ═══════════════════════════════════════════════
story.append(PageBreak())
story += banner("EXAM Q & A  —  AI Unit 3 & Unit 4",
                "Short Answer (3M)  ·  Medium (7M)  ·  Long Answer (12M)")

story += h1("UNIT 3 — Q & A")
story += h2("A — Short Answer (3 Marks)")

story += qa("What is the Minimax algorithm? What are its time and space complexities?", "3M",
    [("Minimax is a recursive algorithm for choosing the optimal move in a two-player zero-sum game.", False),
     ("MAX player always picks the child with maximum value; MIN player picks minimum value.", True),
     ("It builds the complete game tree using DFS and backs up values from leaf nodes.", True),
     ("Time Complexity: O(b^m) — b=branching factor, m=depth of tree.", True),
     ("Space Complexity: O(bm) — only one path root-to-leaf stored at a time.", True),])

story += qa("What is Alpha-Beta Pruning? Define α and β.", "3M",
    [("Alpha-Beta Pruning is an optimisation of Minimax that prunes branches that cannot affect the result.", False),
     ("α (alpha): The best value MAX can guarantee so far. Maintained by MAX player. Starts at -∞.", True),
     ("β (beta): The best value MIN can guarantee so far. Maintained by MIN player. Starts at +∞.", True),
     ("Prune when α ≥ β (at MIN node) or β ≤ α (at MAX node). Result is identical to full Minimax.", True),
     ("Best case: O(b^(m/2)) — doubles the effective search depth for same computation budget.", True),])

story += qa("What are the levels of NLP? List any four.", "3M",
    [("NLP analysis happens at multiple levels of language abstraction:", False),
     ("Morphological: Structure of words — roots, prefixes, suffixes. 'running' = 'run'+'ing'", True),
     ("Syntactic: Grammar structure. Parse tree showing subject-verb-object relationships.", True),
     ("Semantic: Meaning of words and sentences. Resolving word sense ambiguity.", True),
     ("Pragmatic: Intent and context beyond literal meaning. Sarcasm, implied meaning.", True),
     ("Discourse: Meaning across multiple sentences. Pronoun resolution, coherence.", True),])

story += qa("Differentiate EBL, Learning by Discovery, and Learning by Analogy.", "3M",
    [("EBL (Explanation-Based Learning): Learns general concept from ONE example using domain knowledge. Constructs an explanation of why the example is an instance of the concept.", True),
     ("Learning by Discovery: No training examples. AI autonomously explores problem space and discovers new patterns/concepts (e.g., BACON rediscovered Kepler's laws).", True),
     ("Analogy-based Learning: Maps structure of a solved problem to a new problem. Solar system → atom, water flow → electricity.", True),])

story += h2("B — Medium Answer (7 Marks)")

story += qa("Explain Neural Networks. Describe the Backpropagation algorithm in detail.", "7M",
    [("An Artificial Neural Network (ANN) consists of layers of connected artificial neurons: input layer, hidden layers, output layer.", False),
     ("Each neuron: computes z = Σ(wᵢxᵢ) + b, then applies activation function f(z) to get output.", True),
     ("Activation functions: Step (binary), Sigmoid (0-1), Tanh (-1 to 1), ReLU (0 to ∞).", True),
     ("Backpropagation — 5 steps:", False),
     ("Step 1 — Forward pass: Feed input through network, compute output ŷ layer by layer.", True),
     ("Step 2 — Compute loss: L = (y−ŷ)² for regression; cross-entropy for classification.", True),
     ("Step 3 — Backward pass: Apply chain rule to compute ∂L/∂w for every weight.", True),
     ("Step 4 — Update weights: w ← w − η·(∂L/∂w). η = learning rate.", True),
     ("Step 5 — Repeat for all training examples (one epoch). Run many epochs until convergence.", True),
     ("Learning rate too high → overshoot. Too low → slow. Overfitting → use dropout/regularisation.", True),])

story += qa("Explain Genetic Algorithms with all components, operators, and a worked example.", "7M",
    [("Genetic Algorithms (GA) are search algorithms inspired by Darwinian evolution.", False),
     ("Components: Population (set of solutions), Chromosome (one solution), Gene (one element), Fitness Function (quality measure).", True),
     ("GA Steps: 1) Initialise random population. 2) Evaluate fitness. 3) Select parents. 4) Crossover. 5) Mutate. 6) Replace. 7) Repeat.", True),
     ("Selection: Fitter individuals more likely chosen. Methods: Roulette wheel, Tournament selection.", True),
     ("Crossover: Combine two parents at a crossover point. One-point: [A|BCDE] + [a|bcde] → [A|bcde].", True),
     ("Mutation: Randomly flip a gene with small probability (0.01). Maintains genetic diversity, prevents premature convergence.", True),
     ("Elitism: Always keep the best individual in each generation.", True),
     ("Example: Maximise binary string 1s. Initial: 01001011 (fitness=4). After crossover+mutation converges to 11111111 (fitness=8).", True),
     ("Applications: TSP, job scheduling, neural architecture search, parameter optimisation.", True),])

story += h1("UNIT 4 — Q & A")
story += h2("C — Medium Answer (7 Marks)")

story += qa("Explain Fuzzy Logic Systems. Describe the Fuzzy Inference System with an example.", "7M",
    [("Fuzzy Logic allows degrees of truth in [0,1] instead of binary 0/1. Introduced by Lotfi Zadeh (1965).", False),
     ("Crisp Logic: Person is 'tall' or 'not tall'. Fuzzy: Person is 'tall' to degree 0.7.", True),
     ("Fuzzy Sets: Each element has a membership degree μ(x) ∈ [0,1] defined by a membership function.", True),
     ("Operations: AND=min(μA,μB), OR=max(μA,μB), NOT=1-μA.", True),
     ("Fuzzy Inference System (FIS) — 4 steps:", False),
     ("1. Fuzzification: Convert crisp input to fuzzy values. 35°C → HOT=0.7, WARM=0.3", True),
     ("2. Rule Evaluation: Apply IF-THEN rules. IF Hot THEN FanFast (strength 0.7). IF Warm THEN FanMedium (strength 0.3).", True),
     ("3. Aggregation: Combine all rule outputs using max operator.", True),
     ("4. Defuzzification: Convert fuzzy output to crisp value using centroid method: x* = Σ(x·μ)/Σμ → Fan=78%", True),
     ("Applications: ABS brakes, washing machines, traffic control, medical diagnosis.", True),])

story += qa("Explain Expert Systems. What is Forward Chaining and Backward Chaining?", "7M",
    [("An Expert System is an AI program that mimics a human expert using a Knowledge Base and Inference Engine.", False),
     ("Components: Knowledge Base (facts + IF-THEN rules), Inference Engine (reasoning), Working Memory, Explanation Facility, User Interface.", True),
     ("Forward Chaining (Data-Driven): Starts with known facts, applies rules to derive new facts until goal reached.", True),
     ("Example: fever=high, cough=yes → Rule1 fires → suspect=flu → Rule2 fires → diagnosis=influenza.", True),
     ("Used for: monitoring, planning, alerting systems where we start from observations.", True),
     ("Backward Chaining (Goal-Driven): Starts with a hypothesis/goal, works backward to find supporting facts.", True),
     ("Example: Is diagnosis=influenza? → Need suspect=flu → Need fever=high AND cough=yes → Check these facts.", True),
     ("Used for: diagnosis, debugging, proving hypotheses.", True),
     ("Examples: MYCIN (medical), DENDRAL (chemistry), XCON (computer configuration).", True),])

story += qa("Explain Bayesian Networks. How is inference done? Give an example.", "7M",
    [("A Bayesian Network is a probabilistic graphical model (DAG) representing conditional dependencies between variables.", False),
     ("Nodes = random variables. Directed edge A→B means A directly influences B.", True),
     ("Each node has a Conditional Probability Table (CPT): P(node | its parents).", True),
     ("Joint probability factorises as: P(X₁,...,Xₙ) = ∏ P(Xᵢ | parents(Xᵢ)).", True),
     ("Example: Cloudy→Rain, Cloudy→Sprinkler, Rain→WetGrass, Sprinkler→WetGrass.", True),
     ("Inference: Given evidence (observed vars), compute probability of query variable.", True),
     ("P(Rain=T | WetGrass=T): Sum over all states of Cloudy and Sprinkler → result ≈ 0.708.", True),
     ("Methods: Exact inference (Variable Elimination), Approximate (Monte Carlo sampling).", True),
     ("Applications: Medical diagnosis, spam filtering, fault detection, gene networks.", True),])

story += qa("Explain K-Means Clustering Algorithm in detail with a numerical example.", "7M",
    [("K-Means is an unsupervised partitioning algorithm that groups N points into K clusters by minimising WCSS.", False),
     ("Algorithm: 1) Choose K. 2) Initialise K random centroids. 3) Assign each point to nearest centroid (Euclidean distance). 4) Update centroid = mean of cluster. 5) Repeat 3-4 until convergence.", True),
     ("Numerical Example: Points A(1,1), B(1,2), C(2,1), D(8,8), E(9,8), F(8,9). K=2.", True),
     ("Init: C1=(1,1), C2=(8,8). Assign: A,B,C → C1; D,E,F → C2.", True),
     ("Update: C1=mean(A,B,C)=(1.33,1.33). C2=mean(D,E,F)=(8.33,8.33).", True),
     ("Iteration 2: Same assignment → centroids unchanged → CONVERGED!", True),
     ("Choosing K: Use Elbow Method. Plot WCSS vs K. Pick the 'elbow' (bend in curve).", True),
     ("Limitations: Need to specify K, sensitive to initialisation and outliers, assumes spherical clusters.", True),
     ("Applications: Customer segmentation, image compression, document clustering.", True),])

story += h2("D — Long Answer (12 Marks)")

story += qa("Explain Machine Learning completely: types, workflow, algorithms, overfitting, and evaluation metrics.", "12M",
    [("ML Definition: Systems learn from data and improve without being explicitly programmed (Arthur Samuel, 1959).", False),
     ("4 Types: Supervised (labelled data, predict output), Unsupervised (find patterns), Semi-supervised (mixed), Reinforcement (reward-based).", True),
     ("Supervised Algorithms: Linear Regression (predict continuous), Logistic Regression (classify), Decision Tree (if-then splits), SVM (max margin hyperplane), K-NN (nearest neighbours vote), Neural Networks (deep patterns).", True),
     ("Unsupervised: K-Means clustering, Hierarchical clustering, PCA (dimensionality reduction), Autoencoders.", True),
     ("ML Workflow: Problem definition → Data collection → Preprocessing → Feature Engineering → Model selection → Training → Evaluation → Deployment.", True),
     ("Preprocessing: Handle missing values, remove outliers, normalise (MinMax/Z-score), encode categorical variables.", True),
     ("Overfitting: Low train error, HIGH test error. Model memorised training data. Fix: more data, dropout, regularisation (L1/L2), cross-validation.", True),
     ("Underfitting: High error on both. Model too simple. Fix: more features, complex model.", True),
     ("Evaluation Metrics — Classification: Accuracy=(TP+TN)/Total; Precision=TP/(TP+FP); Recall=TP/(TP+FN); F1=2PR/(P+R).", True),
     ("Evaluation — Regression: MSE=Σ(y-ŷ)²/n; RMSE=√MSE; MAE=Σ|y-ŷ|/n.", True),
     ("Cross-validation: K-fold CV splits data into K parts, trains on K-1, tests on 1, rotates. More reliable than single split.", True),
     ("Bias-Variance Tradeoff: High bias=underfitting; High variance=overfitting; Goal=balance both.", True),])

# ── Summary ──────────────────────────────────────────────────────────────
story.append(sp(8))
sumdata = [[Paragraph(
    "<b>Quick Reference — Unit 3 &amp; 4 Key Points</b><br/><br/>"
    "<b>Minimax:</b> MAX picks max child; MIN picks min child. O(b^m). Terminal node has utility value.<br/>"
    "<b>Alpha-Beta:</b> α=MAX lower bound; β=MIN upper bound. Prune when α≥β. O(b^(m/2)) best case.<br/>"
    "<b>NLP Levels:</b> Morphological→Lexical→Syntactic→Semantic→Pragmatic→Discourse<br/>"
    "<b>EBL:</b> 1 example + domain theory → explanation → generalise → new rule.<br/>"
    "<b>GA Steps:</b> Init → Fitness → Select → Crossover → Mutate → Replace → Repeat<br/>"
    "<b>ANN:</b> Input→Hidden(s)→Output. z=Σwx+b, activate. Backprop: forward→loss→backward→update weights.<br/>"
    "<b>Fuzzy FIS:</b> Fuzzify → Rule Eval → Aggregate → Defuzzify (centroid)<br/>"
    "<b>Expert System:</b> KB + Inference Engine. Forward chaining=fact→goal. Backward=goal→facts.<br/>"
    "<b>Bayesian Net:</b> DAG + CPTs. P(X₁..Xₙ)=∏P(Xᵢ|parents). Inference by marginalisation.<br/>"
    "<b>K-Means:</b> Choose K → Init centroids → Assign → Update mean → Repeat. Elbow method for K.<br/>"
    "<b>ML Types:</b> Supervised/Unsupervised/Reinforcement. Metrics: Accuracy/Precision/Recall/F1/RMSE",
    PS('SUM', fontSize=9, textColor=DGRAY, leading=15))]]
st = Table(sumdata, colWidths=[CW])
st.setStyle(TableStyle([
    ('BACKGROUND',(0,0),(-1,-1),VBLUE),
    ('BOX',(0,0),(-1,-1),1.5,DBLUE),
    ('TOPPADDING',(0,0),(-1,-1),10),('BOTTOMPADDING',(0,0),(-1,-1),10),
    ('LEFTPADDING',(0,0),(-1,-1),12),('RIGHTPADDING',(0,0),(-1,-1),12)]))
story.append(st)

# ── Build ──────────────────────────────────────────────────────────────
doc = SimpleDocTemplate(
    "C:/Users/Rishi/OneDrive/Desktop/python/AI_Unit3_Unit4_Notes.pdf",
    pagesize=A4,
    leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
    title="AI Unit 3 & 4 Exam Notes")
doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
print("PDF done!")