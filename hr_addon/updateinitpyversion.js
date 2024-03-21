// standard-version-updater.js
module.exports.readVersion = function (contents) {
  return contents.replace("__version__ = '",'').replace("'",'')
}

module.exports.writeVersion = function (contents, version) {
  return "__version__ = '" + version + "'"
}