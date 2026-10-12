#!/bin/sh
# Construit l'APK Android d'Igna Djongo (une coquille qui affiche le site en ligne).
# Outils téléchargés depuis Maven Central : aapt2 (dans apktool), android-all, dx, apksig.
# Usage : KEYSTORE=chemin/igna.p12 KEYPASS=... sh source/android/build-apk.sh [sortie.apk]
# La clé de signature ne va JAMAIS dans le dépôt : sans la même clé, les membres
# ne pourront pas installer une nouvelle version par-dessus l'ancienne.
set -eu
HERE=$(cd "$(dirname "$0")" && pwd)
OUT=${1:-$HERE/../../igna-djongo.apk}
: "${KEYSTORE:?donner KEYSTORE=chemin du fichier .p12}" "${KEYPASS:?donner KEYPASS}"
ALIAS=${KEYALIAS:-igna}
T=${TOOLS:-$HOME/.cache/igna-apk}
M=https://repo.maven.apache.org/maven2
mkdir -p "$T"
get() { [ -s "$T/$2" ] || curl -fsSL --retry 4 -o "$T/$2" "$M/$1"; }
get org/apktool/apktool-lib/3.0.3/apktool-lib-3.0.3.jar apktool-lib.jar
get org/robolectric/android-all/14-robolectric-10818077/android-all-14-robolectric-10818077.jar android-all.jar
get com/jakewharton/android/repackaged/dalvik-dx/16.0.1/dalvik-dx-16.0.1.jar dx.jar
get com/android/tools/build/apksig/2.3.0/apksig-2.3.0.jar apksig.jar
[ -x "$T/prebuilt/linux/aapt2" ] || (cd "$T" && unzip -oq apktool-lib.jar 'prebuilt/linux/aapt2' 'prebuilt/android-framework.jar' && chmod +x prebuilt/linux/aapt2)

B=$(mktemp -d)
"$T/prebuilt/linux/aapt2" compile --dir "$HERE/res" -o "$B/res.zip"
"$T/prebuilt/linux/aapt2" link -o "$B/base.apk" -I "$T/prebuilt/android-framework.jar" \
  --manifest "$HERE/AndroidManifest.xml" --min-sdk-version 24 --target-sdk-version 34 "$B/res.zip"
mkdir -p "$B/classes"
javac -nowarn --release 8 -cp "$T/android-all.jar" -d "$B/classes" $(find "$HERE/java" -name '*.java') 2>&1 | grep -v -E 'bootstrap|release 8|^[0-9]+ warning' || true
java -cp "$T/dx.jar" com.android.dx.command.Main --dex --min-sdk-version=24 --output="$B/classes.dex" "$B/classes"
python3 "$HERE/tools/align.py" "$B/base.apk" "$B/classes.dex" "$B/aligned.apk"
javac -nowarn -cp "$T/apksig.jar" -d "$B" "$HERE/tools/Sign.java"
java --add-exports java.base/sun.security.x509=ALL-UNNAMED -cp "$B:$T/apksig.jar" Sign "$KEYSTORE" "$KEYPASS" "$ALIAS" "$B/aligned.apk" "$OUT"
python3 "$HERE/tools/align.py" --check "$OUT"
rm -rf "$B"
echo "APK prêt : $OUT"
