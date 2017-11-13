# crass [![Build Status](https://travis-ci.org/surrsurus/crass.svg?branch=master)](https://travis-ci.org/surrsurus/crass) ![Python Version](https://img.shields.io/badge/python-2.7-green.svg) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

crass is an HTML Preprocessor for defining and expanding aliases. 

Have you ever run into a situation where your html tag might have 5 or more classes or ids and you find yourself constantly copying that snippet over and over? Your HTML might get very cluttered, very quickly depending on your CSS libraries. Thankfully, crass allows you to define aliases for all of these class and id combinations to improve overall readability. 

For example, if you ever tried creating webpages using the OpenSAPUI5's CSS, you'll know that your html tags become incredibly cluttered with CSS elements, but with crass, you can make this headache dissapear by assigning common patterns to single word aliases.

crass uses a 'crassfile' that is parsed to form a list of aliases that is compared to your source directory. crass will then search the directory for all aliases in your html files that you created in your crassfile and create a new directory with all of the changes. It will preserve your directory structure, and copy in all files regardless if they are HTML or not. You don't need to make any changes to the structure of your existing website, and since crass only operates on your html files you can continue to use CSS or any CSS preprocessor with crass you want.

## Getting Started

Here's how to get crass set up for usage.

### Prerequisites

1. Make sure Python 2 or Python 3 is installed. crass will work with either, you can check [Travis CI](https://travis-ci.org/surrsurus/crass) for proof. Make sure you download Python for your respective os. crass works with windows, linux, and OSX. [Download Python here](https://www.python.org/downloads/).

crass requires no other dependencies to function, with the exception of pytest for testing. You can install pytest via the command

```
pip install pytest
```

### Running

Crass can be run like this:

```
crass <path to source> <path to crassfile> <path to desired build directory>
```

### Running the Tests

Once you have pytest installed via pip (see above), you can run

```
pytest crass.py
```

to run the testing suite.

### Examples

#### Example crassfile

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

#### Example Website with Aliases

By running 

```crass.py ./example/src/ ./example/example.crass ./example/build/```

 you'll create an example webiste in a `build` directory under `example` that will be created at runtime. Then just open up `index.html` in your browser of choice.

This example in specific shows how OpenUI5 elements can be reduced to aliases to make reading the html files much more programmer-friendly.

## Q&A

Q: Does crass need to see my CSS/Less/Sass?

A: No. crass only assumes you have the expansions for your aliases defined in your css, it does not create any compiled css iteself, only change aliases into their proper epxansions that you define, which can be anything.

Q: Can crass make aliases for CSS/Less/Sass?

A: No. crass only modifies your HTML files. crass will work with CSS and any preprocessor but that's because your aliases defined in the crassfile will only be compared against your HTML file, so you cannot create aliases in that sense.

## License

<img align="center" src="https://pre00.deviantart.net/4938/th/pre/f/2016/070/3/b/mit_license_logo_by_excaliburzero-d9ur2lg.png" alt="MIT" width=100>

This code is released under the MIT LICENSE. All works in this repository are meant to be utilized under this license. You are entitled to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, as long as this permission notice shall be included in all copies or substantial portions of the Software.

