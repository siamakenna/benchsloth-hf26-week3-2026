from pathlib import Path
R=Path(__file__).resolve().parents[2];p=R/'static/index.html';s=p.read_text()
if 'intelligence-pane' in s:raise SystemExit('Already upgraded')
# Archive the exact prior template locally; v5 tag remains authoritative.
(R/'static/index-v5.html').write_text(s)
s=s.replace('</head>','<link rel="stylesheet" href="product/product-v6.css"></head>')
# Actual strings are matched directly, avoiding edits to frozen engines.
s=s.replace('Less clock-watching.<br><em>More room for science.</em>','Give your attention<br><em>a plan.</em>')
s=s.replace('Try the 60-second interactive demo','Explore the live product demo')
s=s.replace('See real Gemma in action','See real Gemma in action')
s=s.replace('Less clock-watching.','Give your attention a plan.')
s=s.replace('More room for science.','Keep the evidence in view.')
marker='</section></div><section id="workbench"'
assert marker in s
panel='''</section><section class="intelligence-pane" aria-labelledby="askTitle"><div class="panel-head"><div><div class="panel-title" id="askTitle">Ask BenchSloth</div><small>03 / INTELLIGENCE · EVIDENCE FIRST</small></div></div><div class="intelligence-body"><div><div class="ask-mode" id="askMode">Recorded Gemma output</div><p class="caption">Ask what needs attention, which note belongs where, or what the source leaves unanswered.</p><div class="ask-prompts" id="askPrompts"></div><form id="askForm" class="ask-input" hidden><label for="askQuestion" class="micro">QUESTION ABOUT THIS SOURCE</label><textarea id="askQuestion" maxlength="500" placeholder="What should I look at when I return?"></textarea><button class="btn" id="askSubmit">Ask local Gemma ↗</button></form><p id="askProgress" class="ask-progress" role="status" aria-live="polite"></p></div><div id="askAnswer" class="ask-answer" aria-live="polite" hidden></div><div class="ask-session"><button class="text-link" id="askHandoff">What needs attention when I return? ↗</button><p class="caption">Current browser facts. Deterministic, no new model inference.</p></div><p class="caption qa-boundary">Gemma selects evidence; the source stays verbatim. Answers cannot start timers or change your plan. A valid citation does not prove a correct interpretation.</p></div></section></div><section id="workbench"'''
s=s.replace(marker,panel)
s=s.replace('data-scene="agent"','data-scene="agent"',1)
s=s.replace('<section class="how"','<div class="journey-strip" aria-label="BenchSloth journey"><span>READ</span><span>UNDERSTAND</span><span>VERIFY</span><span>PLAN</span><span>REST</span><span>RETURN</span></div><section class="how"',1)
s=s.replace('Gemma links notes to the intervals they describe. “During” and “after” can mean very different demands on your attention.','Ask Gemma to find the original evidence behind a question. Inspect its selection, uncertainty and real request before accepting an interpretation.')
s=s.replace('Evidence before a score.</h3>','Does BenchSloth Actually Work?</h3>')
s=s.replace('Read complete evaluation and limitations ↗','Explore every case, answer and failure ↗').replace('Inspect core source ZIP ↗','Optional core source ZIP ↗')
s=s.replace('const REPLAY = false','const REPLAY = false')
s=s.replace("a.href='assets/v5/demo-captioned.webm'","a.href='assets/v6/demo-captioned.webm'")
s=s.replace('</script></body>','</script><script src="product/intelligence-v6.js"></script></body>')
p.write_text(s)
