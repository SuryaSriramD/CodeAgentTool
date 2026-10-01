import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
fun handle(stmt: Statement, input: String, factory: DocumentBuilderFactory) {
factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true)
}
