MAINENTRY=math.tex

# @see https://linux.die.net/man/1/pdflatex
# `-interaction=nonstopmode` sets the interaction mode to nonstop,
#     which makes TeX run without requiring feedback from the user,
#     through the errors.
# `-halt-on-error` ensures TeX exits with an error code
#     when an error is encountered during processing,
#     thus failing the build in Travis CI.
compile:
	latexmk -xelatex -interaction=nonstopmode -halt-on-error -silent ${MAINENTRY}
	./copy.sh

# the following recipe allows the developer to interact
debug:
	xelatex -synctex=1 ${MAINENTRY}

timeit:
	time latexmk -xelatex -synctex=1 -interaction=nonstopmode -halt-on-error -silent ${MAINENTRY}

clean:
	git clean -Xf
