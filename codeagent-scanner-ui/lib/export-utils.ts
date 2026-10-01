export function download(content: string, filename: string, mime = "text/plain;charset=utf-8") {
  const href = URL.createObjectURL(new Blob([content], { type: mime }));
  const link = document.createElement("a"); link.href = href; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(href), 1000);
}
