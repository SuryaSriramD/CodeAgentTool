fn handle(input: &str, connection: rusqlite::Connection) {
connection.prepare(&format!("SELECT * FROM users ORDER BY {}",input));
}
