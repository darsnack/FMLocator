#! /usr/bin/env python

import BaseHTTPServer
import urlparse
from xml.dom.minidom import Document
import json
import sys
import os
import fnmatch
from v4l2radio import FMRadio, FMRadioUnavailableError, RadioDNSRDSListener


_HOSTNAME = "0.0.0.0"
_PORT = 8080


class RadioHTTPServer(BaseHTTPServer.HTTPServer):
    
    def __init__(self, tuners, server_address, RequestHandlerClass, bind_and_activate=True):
        
        BaseHTTPServer.HTTPServer.__init__(self, server_address, RequestHandlerClass, bind_and_activate)
        
        self.tuners = tuners
        

class RadioHTTPRequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        
        """Respond to a GET request."""
        
        parsed_path = urlparse.urlparse(self.path)
        
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            
            f = open("index.html", 'r')
            self.wfile.write(f.read())
            f.close()
            
        elif parsed_path.path == "/status.xml" or parsed_path.path == "/status.json":
            self.send_response(200)
            if parsed_path.path.endswith("xml"):
                doc = Document()
                radioNode = doc.createElement("radio")
                doc.appendChild(radioNode)
                for i, (tuner, rdnsListener) in enumerate(self.server.tuners):
                    tunerNode = doc.createElement("tuner")
                    radioNode.appendChild(tunerNode)
                    tunerNode.setAttribute("id", str(i))
                    tunerNode.setAttribute("type", "fm")
                    tunerNode.setAttribute("frequency", "%.2f" % (tuner.get_frequency() / 1000.0))
                    tunerNode.setAttribute("signal", "%.2f" % tuner.get_signal_strength())
                    rdsNode = doc.createElement("rds")
                    tunerNode.appendChild(rdsNode)
                    if tuner.rds.ecc is not None:
                        rdsNode.setAttribute("ecc", tuner.rds.ecc[2:])
                    if tuner.rds.pi is not None:
                        rdsNode.setAttribute("pi", tuner.rds.pi[2:])
                    if tuner.rds.ps is not None:
                        rdsNode.setAttribute("ps", tuner.rds.ps)
                    if tuner.rds.rt is not None:
                        rdsNode.setAttribute("rt", tuner.rds.rt)
                    if rdnsListener.authFqdn is not None:
                        radiodnsNode = doc.createElement("radiodns")
                        tunerNode.appendChild(radiodnsNode)
                        radiodnsNode.setAttribute("authFqdn", rdnsListener.authFqdn)
                        for app, results in rdnsListener.apps.items():
                            for result in results:
                                resultNode = doc.createElement(app)
                                radiodnsNode.appendChild(resultNode)
                                resultNode.setAttribute("target", result["target"])
                                resultNode.setAttribute("port", str(result["port"]))
                                resultNode.setAttribute("priority", str(result["priority"]))
                                resultNode.setAttribute("weight", str(result["weight"]))
                self.send_header("Content-type", "application/xml")
                self.end_headers()
                self.wfile.write(doc.toprettyxml("  ", "\n", "UTF-8"))
            elif parsed_path.path.endswith("json"):
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"radio": {"tuner": []}}
                for i, (tuner, rdnsListener) in enumerate(self.server.tuners):
                    item = {"id": i,
                            "type": "fm",
                            "frequency": "%.2f" % (tuner.get_frequency() / 1000.0),
                            "signal": "%.2f" % tuner.get_signal_strength(),
                            "rds": {}}
                    if tuner.rds.ecc is not None:
                        item["rds"]["ecc"] = tuner.rds.ecc[2:]
                    if tuner.rds.pi is not None:
                        item["rds"]["pi"] = tuner.rds.pi[2:]
                    if tuner.rds.ps is not None:
                        item["rds"]["ps"] = tuner.rds.ps
                    if tuner.rds.rt is not None:
                        item["rds"]["rt"] = tuner.rds.rt
                    if rdnsListener.authFqdn is not None:
                        radiodns = {"authFqdn": rdnsListener.authFqdn}
                        for app, results in rdnsListener.apps.items():
                            radiodns[app] = []
                            for result in results:
                                radiodns[app].append({"target": result["target"],
                                                      "port": str(result["port"]),
                                                      "priority": str(result["priority"]),
                                                      "weight": str(result["weight"])})
                        item["radiodns"] = radiodns
                    response["radio"]["tuner"].append(item)
                self.wfile.write(json.dumps(response, indent=2))
                
        elif parsed_path.path == "/configure.xml" or parsed_path.path == "/configure.json":
            results = []
            query = urlparse.parse_qs(parsed_path.query)
            if query.has_key("method"):
                if query.has_key("tuner"):
                    try:
                        tunerIndex = int(query["tuner"][0])
                        tuner = self.server.tuners[tunerIndex][0]
                    except IndexError:
                        results.append(("tuner", "fail"))
                else:
                    tuner = self.server.tuners[0][0]
                    
                for i, method in enumerate(query["method"]):
                    if method == "fm.setFrequency":
                        try:
                            frequency = int(float(query["frequency"][i]) * 1000)
                            tuner.set_frequency(frequency)
                            results.append((method, "ok"))
                        except Exception:
                            results.append((method, "fail"))
                    else:
                        results.append((method, "fail"))
            else:
                results.append(("method", "fail"))
                
            self.send_response(200 if len(results) == 0 else 500)
            if parsed_path.path.endswith("xml"):
                doc = Document()
                resultsNode = doc.createElement("results")
                doc.appendChild(resultsNode)
                for method, status in results:
                    resultNode = doc.createElement("result")
                    resultsNode.appendChild(resultNode)
                    resultNode.setAttribute("method", method)
                    resultNode.setAttribute("status", status)
                self.send_header("Content-type", "application/xml")
                self.end_headers()
                self.wfile.write(doc.toprettyxml("  ", "\n", "UTF-8"))
            elif parsed_path.path.endswith("json"):
                self.send_header("Content-type", "application/json")
                self.end_headers()
                response = {"results": {"result": []}}
                for method, status in results:
                    response["results"]["result"].append({"method": method,
                                                          "status": status})
                self.wfile.write(json.dumps(response, indent=2))
                
        else:
            self.send_error(404, "Not Found")
            
            
if __name__ == '__main__':
    devices = []
    for file in os.listdir("/dev"):
        if fnmatch.fnmatch(file, "radio*"):
            devices.append(file)
            
    if len(devices) == 0:
        print "No tuners found"
        sys.exit(1)
        
    print "Starting tuner%s..." % ('s' if len(devices) > 1 else '')
    
    tuners = []
    for i, device in enumerate(devices):
        try:
            tuner = FMRadio("/dev/%s" % device)
            tuner.set_frequency(87.5 * 1000.0)
            listener = RadioDNSRDSListener()
            tuner.rds.add_listener(listener)
            tuners.append((tuner, listener))
#            tuner.rds.add_listener(IcecastMetaRDSDecoderListener())
        except FMRadioUnavailableError:
            pass
            
    if len(tuners) == 0:
        print "No tuners are available"
        sys.exit(1)
        
    print "Starting HTTP server..."
    
    httpd = RadioHTTPServer(tuners, (_HOSTNAME, _PORT), RadioHTTPRequestHandler) 
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
        
    print "Stopping HTTP server..."
    httpd.server_close()
    
    print "Stopping tuner%s..." % ('s' if len(devices) > 1 else '')
    for tuner, listener in tuners:
        tuner.close()
        
