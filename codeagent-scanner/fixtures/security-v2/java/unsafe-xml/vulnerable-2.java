import java.sql.*;
import javax.xml.parsers.*;
class Example { void handle(Statement stmt, String input, DocumentBuilderFactory factory) { factory.setFeature("http://xml.org/sax/features/external-general-entities", true); } }
