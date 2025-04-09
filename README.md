# 0xffae

`0xffae` is a project developed to visualize the information used by PRONOM to
identify file-formats using emoji.

`0xffae` might be used as a whimsical diversion during the course of training
folks about file-format signature development, or you might find other uses
for it.

Ideas and pull-requests welcome.

## Technology

Richard Lehane's builder is the most mature component exporting
information about PRONOM in one place, and providing access to the
skeleton-suite.

* [Builder][builder-1].

Radare first released an emoji export in 2016. It is a powerful hex editor,
unfortunately I don't have a lot of excuses to work with hex at present and
so I am not as au-fait with it as I would like. Folks interested in what is
essentially a glorified demo of a narrow-band of its functionality may be
interested in looking into it further.

* [radare2][radare-1].

PyScript is an open source platform for Python in the browser and allows us
to run Python client-side separating many of the concerns of privacy and
security into something between only you and your browser. I relish the
opportunity to explore it further.

* [pyscript][pyscript-1].

[pyscript-1]: https://pyscript.net/
[builder-1]: https://github.com/richardlehane/builder
[radare-1]: https://rada.re/n/

## Background

The project was first conceived of in 2016 but sat dormant on a server due to
a lack of sophistication implementing things.

2025 brings PyScript and an opportunity to use it to further familarize myself
with the technology and finally write myself a random page generator.

## Random page generation

The script here should be pretty flexible if you'd like to create your own
random page generator. There are easier ways than using a database of course so
you might ignore that part but the database also gives us some nice
possibilities.

## License

zLib unless otherwise convinced.
