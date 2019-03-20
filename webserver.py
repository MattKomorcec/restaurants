from http.server import HTTPServer, BaseHTTPRequestHandler
import cgi
from sqlalchemy.orm import sessionmaker
from database_configuration import engine, Restaurant

Session = sessionmaker(bind=engine)
session = Session()


class WebServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                restaurants = session.query(Restaurant).all()

                output = "<html><body>"
                output += "<h1>List of restaurants</h1>"
                output += "<a href='/restaurants/new'>Create a new restaurant</a>"
                output += "<hr />"
                for restaurant in restaurants:
                    output += "<h3>{}</h3>".format(restaurant.name)
                    output += "<a href='/restaurant/{}/edit'>Edit</a> | ".format(restaurant.id)
                    output += "<a href='/restaurant/{}/delete'>Delete</a>".format(restaurant.id)
                    output += "<hr />"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            if self.path.endswith('/restaurants/new'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = "<html><body>"
                output += "<h1>Create a new restaurant</h1>"
                output += "<form method='POST' action='/restaurants/new' enctype='multipart/form-data'>"
                output += "<input type='text' name='restaurant_name' />"
                output += "<input type='submit' value='Create' />"
                output += "</form>"
                output += "<a href='/restaurants'>Go back</a>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            if self.path.endswith('/edit'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                res_id = self.path.split("/")[2]

                restaurant = session.query(Restaurant).get(res_id)

                output = "<html><body>"
                output += "<h1>Edit a restaurant</h1>"
                output += "<form method='POST' action='/restaurant/{}/edit' enctype='multipart/form-data'>".format(restaurant.id)
                output += '<input type="text" name="restaurant_name" value="{}" />'.format(restaurant.name)
                output += "<input type='submit' value='Update' />"
                output += "</form>"
                output += "<a href='/restaurants'>Go back</a>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            if self.path.endswith('/delete'):
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                res_id = self.path.split("/")[2]

                restaurant = session.query(Restaurant).get(res_id)

                output = "<html><body>"
                output += "<h1>Delete a restaurant?</h1>"
                output += "<form method='POST' action='/restaurant/{}/delete' enctype='multipart/form-data'>".format(restaurant.id)
                output += "<input type='submit' value='Delete' />"
                output += "</form>"
                output += "<a href='/restaurants'>Go back</a>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

        except IOError:
            self.send_error(404, "File not found!")

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers['Content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurant_name')

                    new_res = Restaurant(name=restaurant_name[0])
                    session.add(new_res)
                    session.commit()

                    output = "<html><body>"
                    output += "<h1>Create a new restaurant</h1>"
                    output += "<form method='POST' action='/restaurants/new' enctype='multipart/form-data'>"
                    output += "<input type='text' name='restaurant_name' />"
                    output += "<input type='submit' value='Create' />"
                    output += "</form>"
                    output += "<h2>Restaurant created!</h2>"
                    output += "<a href='/restaurants'>Go back</a>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                    return

            if self.path.endswith('/edit'):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers['Content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len

                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_name = fields.get('restaurant_name')

                    res_id = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).get(res_id)
                    restaurant.name = restaurant_name[0]

                    session.commit()

                    output = "<html><body>"
                    output += "<h1>Edit a restaurant</h1>"
                    output += "<form method='POST' action='/restaurants/new' enctype='multipart/form-data'>"
                    output += '<input type="text" name="restaurant_name" value="{}" />'.format(restaurant.name)
                    output += "<input type='submit' value='Update' />"
                    output += "</form>"
                    output += "<h2>Restaurant updated!</h2>"
                    output += "<a href='/restaurants'>Go back</a>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                    return

            if self.path.endswith('/delete'):
                self.send_response(301)
                self.end_headers()

                ctype, pdict = cgi.parse_header(self.headers['Content-type'])

                pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
                content_len = int(self.headers.get('Content-length'))
                pdict['CONTENT-LENGTH'] = content_len

                if ctype == 'multipart/form-data':
                    res_id = self.path.split("/")[2]
                    restaurant = session.query(Restaurant).get(res_id)

                    session.delete(restaurant)
                    session.commit()

                    output = "<html><body>"
                    output += "<h1>Restaurant deleted!</h1>"
                    output += "<a href='/restaurants'>Go back</a>"
                    output += "</body></html>"
                    self.wfile.write(output.encode())
                    return

        except IOError:
            print("There was an error", IOError)


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web server running on port {}".format(port))
        server.serve_forever()

    except KeyboardInterrupt:
        print("Server stopped!")
        server.socket.close()


if __name__ == '__main__':
    main()
