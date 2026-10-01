import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
fun handle(stmt: Statement, input: String, factory: DocumentBuilderFactory) {
factory.setFeature("http://xml.org/sax/features/external-general-entities", false)
}
