import java.sql.*;
import javax.xml.parsers.*;
class Example { void handle(Statement stmt, String input, DocumentBuilderFactory factory) { factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true); } }
