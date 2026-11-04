const params = new URLSearchParams(location.hash.slice(1));
const en = (params.get("lang") || new URLSearchParams(location.search).get("lang")) === "en";
const copy = {
  back: ["返回官网", "Back to website"], title: ["说说你的想法", "Tell me what you think"],
  intro: ["发现 bug、想要的功能、使用中不顺手的地方，都可以告诉我。", "Found a bug, want a feature, or have something that could work better? Let me know."],
  message: ["想说点什么？", "What would you like to share?"], email: ["邮箱", "Email"], optional: ["（选填）", "(optional)"],
  screenshot: ["截图", "Screenshot"], addImage: ["添加一张问题截图", "Add a screenshot"],
  uploadHelp: ["粘贴或拖到这里也可以。请先遮盖敏感信息；PNG、JPEG 或 WebP，不超过 5 MB。", "You can also paste or drop an image. Hide sensitive information first. PNG, JPEG or WebP, up to 5 MB."],
  remove: ["移除", "Remove"], privacy: ["请勿提交密码、密钥或与问题无关的敏感信息。反馈仅用于排查问题和改进产品。", "Do not include passwords, keys or unrelated sensitive information. Feedback is only used to resolve issues and improve the app."],
  privacyLink: ["隐私说明", "Privacy"], send: ["发送反馈", "Send feedback"], sending: ["正在发送…", "Sending…"],
  received: ["反馈已收到", "Feedback received"], thanks: ["谢谢你，我会认真查看。", "Thank you. I’ll take a look."], again: ["再写一条", "Send another"],
  format: ["请使用 PNG、JPEG 或 WebP 图片。", "Please use a PNG, JPEG or WebP image."], size: ["图片不能超过 5 MB，请缩小后重试。", "The image is larger than 5 MB. Please resize it and try again."],
  failed: ["暂时没能发送，请稍后重试。你填写的内容已保留。", "Could not send right now. Please try again shortly. Your draft is still here."],
  tooFrequent: ["发送太频繁，请等一分钟再试。你填写的内容已保留。", "Please wait a minute before sending again. Your draft is still here."],
  imageFailedTitle: ["文字已收到，截图未上传成功", "Message received; screenshot upload failed"],
  imageFailed: ["你的文字反馈已保存，无需重复发送。需要补充截图时，可以再提交一条并注明原问题。", "Your message was saved, so there is no need to resend it. You can send a follow-up with the screenshot if needed."],
};
const t = (key) => copy[key][en ? 1 : 0];
const $ = (id) => document.getElementById(id);
document.querySelectorAll("[data-copy]").forEach((el) => { el.textContent = t(el.dataset.copy); });
if (en) {
  document.documentElement.lang = "en";
  document.title = "Feedback · OpenDuckFrame";
  $("message").placeholder = "For example: what happened after enabling frame generation, or a feature you would like…";
  $("email").placeholder = "Leave an email if you would like me to be able to contact you";
  $("preview-image").alt = "Screenshot to send";
  document.querySelectorAll('.feedback-header a').forEach((a) => { a.href = "/en/"; });
}
const context = { version: (params.get("version") || "").slice(0, 32), system: (params.get("system") || "").slice(0, 240) };
if (context.version || context.system) {
  $("context").textContent = [context.version ? `${en ? "App version" : "应用版本"} ${context.version}` : "", context.system].filter(Boolean).join(" · ") + (en ? " — included with your feedback" : " · 将随反馈发送");
  $("context").hidden = false;
}
let image = null;
let previewURL = null;
let busy = false;
function updateSubmit() { $("submit").disabled = busy || !$("message").value.trim(); }
function showImageError(message) { $("image-error").textContent = message; $("image-error").hidden = !message; }
function setImage(file) {
  showImageError("");
  if (file && !["image/png", "image/jpeg", "image/webp"].includes(file.type)) { showImageError(t("format")); return; }
  if (file && file.size > 5 * 1024 * 1024) { showImageError(t("size")); return; }
  if (previewURL) URL.revokeObjectURL(previewURL);
  image = file;
  previewURL = file ? URL.createObjectURL(file) : null;
  $("upload-empty").hidden = !!file;
  $("upload-preview").hidden = !file;
  if (file) { $("preview-image").src = previewURL; $("image-name").textContent = file.name; }
  else { $("preview-image").removeAttribute("src"); $("image-name").textContent = ""; $("screenshot").value = ""; }
}
$("message").addEventListener("input", () => { $("count").textContent = $("message").value.length; updateSubmit(); });
$("screenshot").addEventListener("change", () => setImage($("screenshot").files[0] || null));
$("remove-image").addEventListener("click", () => setImage(null));
const zone = $("dropzone");
zone.addEventListener("dragover", (event) => { event.preventDefault(); zone.classList.add("drag-over"); });
zone.addEventListener("dragleave", () => zone.classList.remove("drag-over"));
zone.addEventListener("drop", (event) => { event.preventDefault(); zone.classList.remove("drag-over"); if (event.dataTransfer.files.length) setImage(event.dataTransfer.files[0]); });
document.addEventListener("paste", (event) => {
  const file = Array.from(event.clipboardData?.files || []).find((f) => f.type.startsWith("image/"));
  if (file && !$("feedback-form").hidden && !busy) { event.preventDefault(); setImage(file); }
});
function imageData(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve({ data: reader.result.split(",")[1] });
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}
$("feedback-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy || !$("feedback-form").reportValidity()) return;
  busy = true; updateSubmit(); $("submit").textContent = t("sending"); $("submit-error").hidden = true;
  $("feedback-form").setAttribute("aria-busy", "true");
  try {
    const payload = { message: $("message").value.trim(), email: $("email").value.trim(), ...context };
    if (image) payload.image = await imageData(image);
    const response = await fetch("/api/feedback", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    const result = await response.json();
    if (!response.ok || !result.ok) throw new Error(response.status === 429 ? "tooFrequent" : "failed");
    $("success-title").textContent = t(result.image_failed ? "imageFailedTitle" : "received");
    $("success-message").textContent = t(result.image_failed ? "imageFailed" : "thanks");
    $("feedback-form").hidden = true; $("success").hidden = false;
    $("success-title").setAttribute("tabindex", "-1"); $("success-title").focus();
  } catch (error) {
    $("submit-error").textContent = t(error.message === "tooFrequent" ? "tooFrequent" : "failed"); $("submit-error").hidden = false;
  } finally {
    busy = false; updateSubmit(); $("submit").textContent = t("send"); $("feedback-form").removeAttribute("aria-busy");
  }
});
$("write-again").addEventListener("click", () => {
  $("feedback-form").reset(); setImage(null); $("count").textContent = "0"; updateSubmit();
  $("success").hidden = true; $("feedback-form").hidden = false; $("message").focus();
});
