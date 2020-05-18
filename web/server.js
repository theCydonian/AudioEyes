//imports
var http = require('http');
var fs = require('fs');
var url = require('url');
var crypto = require('crypto');

const { parse } = require('querystring');

//define url paths
var urls = {
  '/': "./html/index.html"
};

//defines potential types
var types = {
  'html': "text/html",
  'css': "text/css"
}

// Command Line Arg Parsing
console.log("Parsing command line arguments");
var args = process.argv.slice(2);
var port = 8888;
var set = false;
for (var i = 0; i < args.length; i++) {
  if ((args[i] == "-p" || args[i] == "--port") && args.length >= i) {
    if (args[i+1][0] != "-") {
      port = args[i+1];
      console.log("Found port argument " + port);
      set = true;
    }
  }
}
if (!set) {
  console.log("No port found");
  console.log("Defaulting to port 8888");
}



const server = http.createServer(function (req, res) {

  console.log('\nReceived HTTP Request');

  if (req.method == 'GET') {

    console.log('Req Type: GET');

    // URL Parsing
    var parsed = url.parse(req.url, true);
    console.log('pathname: ' + parsed.pathname);

    var file = urls[parsed.pathname];
    var path = parsed.pathname;
    console.log(path.split('/'));
    if (!file) {
      if (path.split('/')[1] == 'getFromHash') {
      	file = './saved_imgs/' + path.split('/')[2] + '.png';
      } else {
      	file = '.' + parsed.pathname;
  	  }
    }
    console.log('file: ' + file);

    // defines file type
    var type = file.split('.');
    if (type.length < 3) {
      res.writeHead(404, {'Content-Type': 'text/html'});
      console.log("resource not found!\n");
      return res.end("404 Not Found");
    } else {
      type = types[type[2].toLowerCase()];
      if (type) {
        console.log("type: " + type);
      }
    }

    // reads the file
    fs.readFile(file, function(err, data) {
      if (err) {
        res.writeHead(404, {'Content-Type': 'text/html'});
        console.log("resource not found!\n");
        return res.end("404 Not Found");
      }
      if (type) {
        res.writeHead(200, {'Content-Type': type});
      }
      res.write(data);

      return res.end();
    });

  } else if (req.method == 'POST') {

    console.log('Req Type: POST');
    // URL Parsing
    var parsed = url.parse(req.url, true);
    console.log('pathname: ' + parsed.pathname);

   	var buffer_array = [];
   	var length = 0;
    req.on('data', function (data) {
        buffer_array.push(data);
        length += data.length;
        // 100MB limit
        if (length > 1e8) { 
            // FLOOD ATTACK OR FAULTY CLIENT, NUKE REQUEST
            req.connection.destroy();
        }
    });
    req.on('end', () => {
    	img = Buffer.concat(buffer_array);
    	var hash = crypto.createHash('sha256').update(img).digest('base64');
    	console.log('hash: ' + hash);
    	// open the file to write buffer data
		fs.open('./saved_imgs/' + hash + '.png', 'w', function(err, fd) {
		    if (err) {
		        throw 'could not open file: ' + err;
		    }

		    fs.write(fd, img, 0, img.length, null, function(err) {
		        if (err) throw 'error writing file: ' + err;
		        fs.close(fd, function() {
		            console.log('wrote the file successfully');
		        });
		        res.end(hash)
		    });
		});
    });
  }
});

// Starts up server
const host = '127.0.0.1';
console.log("\nInitializing server on port " + port + "\n");
server.listen(port, host);
