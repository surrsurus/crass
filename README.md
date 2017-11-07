# crass

[![Build Status](https://travis-ci.org/surrsurus/gazelle.svg?branch=master)](https://travis-ci.org/surrsurus/gazelle) ![Language](https://img.shields.io/badge/language-python-yellow.svg) ![No Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


crass - An HTML Preprocessor for **CR**eating **A**lia**S**e**S**

# Usage

1. Make sure Python2.7 or greater is installed
2. Run `crass.py <source dir> <crassfile> <build dir>`

crass requires no dependencies to function other than your typical python `os` and `sys` tools.

# What does it do?

crass is an HTML Preprocessor for defining and expanding aliases. 

Have you ever run into a situation where your html tag might have 5 or more classes or ids? Your HTML might get very cluttered, very quickly depending on your CSS libraries. Thankfully, crass allows you to define aliases for all of these class and id combinations you might include in your html tags to improve overall readability. 

For example, if you ever tried creating webpages using the OpenSAPUI5's CSS, you'll know that your html tags become incredibly cluttered with CSS elements, but with crass, you can make this headache dissapear.

crass uses a 'crassfile' that is parsed to form a list of aliases that is compared to your source directory. crass will then search the directory for all aliases in your html files that you created in your crassfile and create a new directory with all of the changes. It will preserve your directory structure, and copy in all files regardless if they are HTML or not. You don't need to make any changes to the structure of your existing website, and since crass only operates on your html files you can continue to use CSS or any CSS preprocessor with crass you want.

# Example crassfile

Here is an example of a typical crassfile

```
// my_crassfile.crass
// Doesn't have to have the .crass extension, however, as long as the file is in this format
// This is a comment

// Here is an example id alias
#id-alias = id1 id2 id3

// And an example class alias
.class-alias = class1 class2 class3
```

By giving this file to crass, it will compare it to your HTML files and replace instances of `class="class-alias"` and `id="id-alias"` with the expansion to become `class="class1 class2 class3"` and `id="id1 id2 id3"` respectively.

# Example Website with Aliases

By running `crass.py ./example/src/ ./example/example.crass ./example/build/` you'll create an example webiste in a `build` directory under `example` that will be created at runtime. Then just open up `index.html` in your browser of choice.

This example in specific shows how OpenUI5 elements can be reduced to aliases to make reading the html files much more programmer-friendly.

# Running Tests

Run `pip install -U pytest` then `pytest tests.py`

# Q&A

Q: Does crass need to see my CSS/Less/Sass?

A: No. crass only assumes you have the expansions for your aliases defined in your css, it does not create any compiled css iteself, only change aliases into their proper epxansions that you define, which can be anything.

Q: Can crass make aliases for CSS/Less/Sass?

A: No. crass only modifies your HTML files. crass will work with CSS and any preprocessor but that's because your aliases defined in the crassfile will only be compared against your HTML file, so you cannot create aliases in that sense.

