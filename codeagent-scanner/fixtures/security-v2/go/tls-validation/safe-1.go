package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
cfg := &tls.Config{InsecureSkipVerify: false}
_ = cfg
}
