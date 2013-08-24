var alwaysReplace = {};
var neverReplace = [];

exports.map = function(tokens, str) {
  str = replaceTokens(alwaysReplace, str);
  str = replaceTokens(tokens, str);
  return str;
}

exports.always = function(tokens) {
  for (key in tokens) {
    alwaysReplace[key] = tokens[key];
  }
}

exports.never = function(key) {
  neverReplace.push(key);
}

function replaceAll(find, replace, str) {
  return str.replace(new RegExp(find, 'g'), replace);
}

function replaceTokens(tokens, str) {
  for (key in tokens) {
    if (neverReplace.indexOf(key) == -1) {
      str = replaceAll("{" + key + "}", tokens[key], str);
    }
  }
  return str;
}

if (process.argv[2] == "testmjs") {
  var testString = "{replaceme} - {ignoreme} - {!!ERROR!!}";
  var expectedResult = "replacedme - {ignoreme} - replaced!";
  exports.always({"replaceme" : "replacedme"});
  exports.always({"ignoreme" : "!!ERROR!!"});
  exports.never("ignoreme");
  var result = exports.map({"!!ERROR!!" : "replaced!"}, testString);
  if (result == expectedResult) {
    console.log("Test passing.");
  } else {
    console.log("Test failing:");
    console.log(result);
  }
}