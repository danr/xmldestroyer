
all: tutorial.pdf index.html

.PHONY: all upload

tutorial.pdf: tutorial.md
	pandoc $< -o $@ -t beamer -H settings.tex --latex-engine=xelatex --latex-engine-opt=-shell-escape

index.html: index.md
	pandoc $< -o $@ -T 'xmldestroyer exercises'

upload:
	scp *html *pdf *xml demo:/export/htdocs/dan/xmldestroyer
