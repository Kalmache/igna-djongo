package app.igna.djongo;

import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.print.PrintAttributes;
import android.print.PrintManager;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

/**
 * Igna Djongo : l'appli Android affiche le site en ligne, pour que chaque
 * mise à jour du site arrive sans réinstaller. Conçue par M.M.B.T · 2026.
 */
public class MainActivity extends Activity {
    static final String HOST = "kalmache.github.io";
    static final String HOME = "https://kalmache.github.io/igna-djongo/";
    static final int PICK_FILE = 1;

    WebView web;
    ValueCallback<Uri[]> pending;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setAllowFileAccess(false);
        s.setMediaPlaybackRequiresUserGesture(true);
        s.setSupportMultipleWindows(false);
        s.setUserAgentString(s.getUserAgentString() + " IgnaDjongoApp/1.0");
        CookieManager.getInstance().setAcceptCookie(true);
        CookieManager.getInstance().setAcceptThirdPartyCookies(web, true);

        web.addJavascriptInterface(new Bridge(), "IgnaApp");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new Chrome());

        if (state != null) web.restoreState(state);
        if (web.getUrl() == null) web.loadUrl(HOME);
    }

    @Override
    protected void onSaveInstanceState(Bundle out) {
        super.onSaveInstanceState(out);
        web.saveState(out);
    }

    @Override
    public void onBackPressed() {
        if (web.canGoBack()) web.goBack();
        else super.onBackPressed();
    }

    static boolean inside(Uri u) {
        return "https".equals(u.getScheme()) && HOST.equals(u.getHost())
                && u.getPath() != null && u.getPath().startsWith("/igna-djongo");
    }

    /** WhatsApp, Facebook, téléphone… s'ouvrent dans l'appli du téléphone. */
    void openOutside(Uri u) {
        Intent i = "tel".equals(u.getScheme())
                ? new Intent(Intent.ACTION_DIAL, u)
                : new Intent(Intent.ACTION_VIEW, u);
        try {
            startActivity(i);
        } catch (ActivityNotFoundException e) {
            Toast.makeText(this, "Aucune appli pour ouvrir ce lien", Toast.LENGTH_SHORT).show();
        }
    }

    class Client extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
            Uri u = r.getUrl();
            if (inside(u)) return false;
            openOutside(u);
            return true;
        }

        @Override
        public void onPageFinished(WebView v, String url) {
            // Copier et imprimer passent par le téléphone (le navigateur intégré ne sait pas le faire seul).
            v.evaluateJavascript("(function(){if(window.__igna)return;window.__igna=1;"
                    + "try{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:function(t){IgnaApp.copy(String(t));return Promise.resolve();}}});}catch(e){}"
                    + "window.print=function(){IgnaApp.print();};})();", null);
        }

        @Override
        public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
            if (!r.isForMainFrame()) return;
            String page = "<!doctype html><html lang='fr'><meta name='viewport' content='width=device-width,initial-scale=1'>"
                    + "<body style='font-family:sans-serif;background:#F1F5F2;color:#163;text-align:center;padding:60px 24px'>"
                    + "<h2 style='color:#0E5A4A'>Igna Djongo</h2><p>Pas de connexion internet pour le moment.</p>"
                    + "<p><button style='background:#0E5A4A;color:#fff;border:0;border-radius:12px;padding:14px 24px;font-size:17px' "
                    + "onclick=\"location.href='" + HOME + "'\">Réessayer</button></p>"
                    + "<p style='color:#889;font-size:12px;margin-top:40px'>Conçue par M.M.B.T · 2026</p></body></html>";
            v.loadDataWithBaseURL(HOME, page, "text/html", "utf-8", null);
        }
    }

    class Chrome extends WebChromeClient {
        @Override
        public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams p) {
            if (pending != null) pending.onReceiveValue(null);
            pending = cb;
            Intent i = new Intent(Intent.ACTION_GET_CONTENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("image/*");
            try {
                startActivityForResult(Intent.createChooser(i, "Choisir une photo"), PICK_FILE);
            } catch (ActivityNotFoundException e) {
                pending = null;
                return false;
            }
            return true;
        }
    }

    @Override
    protected void onActivityResult(int req, int res, Intent data) {
        if (req != PICK_FILE || pending == null) {
            super.onActivityResult(req, res, data);
            return;
        }
        pending.onReceiveValue(WebChromeClient.FileChooserParams.parseResult(res, data));
        pending = null;
    }

    class Bridge {
        @JavascriptInterface
        public void copy(final String text) {
            runOnUiThread(new Runnable() {
                public void run() {
                    ClipboardManager cm = (ClipboardManager) getSystemService(Context.CLIPBOARD_SERVICE);
                    cm.setPrimaryClip(ClipData.newPlainText("Igna Djongo", text));
                }
            });
        }

        @JavascriptInterface
        public void print() {
            runOnUiThread(new Runnable() {
                public void run() {
                    PrintManager pm = (PrintManager) getSystemService(Context.PRINT_SERVICE);
                    pm.print("Igna Djongo", web.createPrintDocumentAdapter("Igna Djongo"),
                            new PrintAttributes.Builder().build());
                }
            });
        }
    }
}
