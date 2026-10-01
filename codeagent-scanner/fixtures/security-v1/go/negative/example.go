package fixture
import "os/exec"
func run(input string) { exec.Command("echo", input) }
