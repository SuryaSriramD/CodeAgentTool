import java.sql.Statement
import javax.xml.parsers.DocumentBuilderFactory
object Example { def handle(stmt: Statement, input: String, factory: DocumentBuilderFactory): Unit = {
factory.setFeature("http://xml.org/sax/features/external-parameter-entities", false)
} }
