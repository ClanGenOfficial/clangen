import argparse
import os
import shutil
import subprocess
import sys
import json


APP_NAME = "Clan Gen"
BUNDLE_ID = "com.clangen.clangen"
PYGAME_CE_VERSION = "2.5.6"

def run_cmd(cmd, check=True):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check)
    return result

def main():
    parser = argparse.ArgumentParser(description="Build ClanGen for iOS")
    # By default we will clean the old template to ensure a fresh build
    parser.add_argument("--clean", action="store_true", help="Remove existing pygame-ios-template before building", default=True)
    parser.add_argument("--target", choices=["simulator", "ios"], default="simulator", help="Target platform (simulator or ios)")
    args = parser.parse_args()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    template_dir = os.path.join(project_dir, "pygame-ios-template")

    if args.clean and os.path.exists(template_dir):
        print("Cleaning old template directory...")
        shutil.rmtree(template_dir)

    # 1. Run the pygame-ios template generator
    print("Generating Xcode project using custom local pygame-ios template...")
    
    zip_path = "/Users/jpollak/src/jbcpollak/pygame-ios-templates/dist/pygame-ios-template-2.5.6.zip"
    if not os.path.exists(zip_path):
        print(f"Error: Custom template zip not found at {zip_path}", file=sys.stderr)
        sys.exit(1)

    if os.path.exists(template_dir):
        print("Cleaning old template directory...")
        shutil.rmtree(template_dir)
        
    os.makedirs(template_dir, exist_ok=True)
    import zipfile
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(template_dir)
        
    app_dir = os.path.join(template_dir, "pygame-ios", "app", "pygame-ios")
    os.makedirs(app_dir, exist_ok=True)
    
    # Copy all files from current dir to app dir, ignoring the template dir itself
    ignore_func = shutil.ignore_patterns('pygame-ios-template', '.git', '.venv', '__pycache__')
    for item in os.listdir(project_dir):
        if item in ['pygame-ios-template', '.git', '.venv', '__pycache__']:
            continue
        s = os.path.join(project_dir, item)
        d = os.path.join(app_dir, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, ignore=ignore_func)
        else:
            shutil.copy2(s, d)

    # Ensure the directory was created
    if not os.path.exists(template_dir):
        print(f"Error: pygame-ios failed to create the template directory at {template_dir}", file=sys.stderr)
        sys.exit(1)

    # 1.5. Remove the .venv directory that pygame-ios created
    # This prevents the macOS binary dependencies like pygame-ce from being injected into the iOS bundle.
    venv_path = os.path.join(template_dir, "pygame-ios", "app", "pygame-ios", ".venv")
    if os.path.exists(venv_path):
        print("Removing macOS .venv directory from Xcode project...")
        shutil.rmtree(venv_path)

    # 2. Patch the Xcode Project File
    pbxproj_path = os.path.join(template_dir, "pygame-ios.xcodeproj", "project.pbxproj")
    if os.path.exists(pbxproj_path):
        print(f"Patching bundle identifier in {pbxproj_path}...")
        with open(pbxproj_path, "r", encoding="utf-8") as f:
            pbx_content = f.read()
        
        # Replace the default bundle ID
        pbx_content = pbx_content.replace(
            "PRODUCT_BUNDLE_IDENTIFIER = com.example.pygame-ios;",
            f"PRODUCT_BUNDLE_IDENTIFIER = {BUNDLE_ID};"
        )
        
        with open(pbxproj_path, "w", encoding="utf-8") as f:
            f.write(pbx_content)
    else:
        print(f"Warning: Could not find {pbxproj_path}")

    # 3. Patch the Info.plist Display Name and Main Module
    plist_path = os.path.join(template_dir, "pygame-ios", "pygame-ios-Info.plist")
    if os.path.exists(plist_path):
        print(f"Patching display name in {plist_path}...")
        with open(plist_path, "r", encoding="utf-8") as f:
            plist_content = f.read()

        # Update MainModule to 'main' so Python executes `main.py`
        plist_content = plist_content.replace(
            "<key>MainModule</key>\n\t<string>ClanGen</string>",
            "<key>MainModule</key>\n\t<string>main</string>"
        )
        plist_content = plist_content.replace(
            "<key>MainModule</key>\n\t<string>pygame-ios</string>",
            "<key>MainModule</key>\n\t<string>main</string>"
        )

        # Update Display Name - try multiple variants to match template
        plist_content = plist_content.replace(
            "<key>CFBundleDisplayName</key>\n\t<string>${PRODUCT_NAME}</string>",
            f"<key>CFBundleDisplayName</key>\n\t<string>{APP_NAME}</string>"
        )
        plist_content = plist_content.replace(
            "<key>CFBundleDisplayName</key>\n\t<string>pygame-ios</string>",
            f"<key>CFBundleDisplayName</key>\n\t<string>{APP_NAME}</string>"
        )
        if "<key>CFBundleDisplayName</key>" not in plist_content:
             plist_content = plist_content.replace(
                "<key>CFBundleName</key>\n\t<string>$(PRODUCT_NAME)</string>",
                f"<key>CFBundleName</key>\n\t<string>$(PRODUCT_NAME)</string>\n\t<key>CFBundleDisplayName</key>\n\t<string>{APP_NAME}</string>"
            )

        # Add UIApplicationSupportsIndirectInputEvents
        if "<key>UIApplicationSupportsIndirectInputEvents</key>" not in plist_content:
            plist_content = plist_content.replace(
                "</dict>\n</plist>",
                "\t<key>UIApplicationSupportsIndirectInputEvents</key>\n\t<true/>\n</dict>\n</plist>"
            )

        with open(plist_path, "w", encoding="utf-8") as f:
            f.write(plist_content)
    else:
        print(f"Warning: Could not find {plist_path}")


    # 4. Patch main.m directory change logic
    main_m_path = os.path.join(template_dir, "pygame-ios", "main.m")
    if os.path.exists(main_m_path):
        print(f"Patching directory target in {main_m_path}...")
        with open(main_m_path, "r", encoding="utf-8") as f:
            main_m_content = f.read()

        main_m_content = main_m_content.replace(
            "NSString *pygameIosPath = [NSString stringWithFormat:@\"%@/app/%@\", [[NSBundle mainBundle] bundlePath], app_module_name];",
            "NSString *pygameIosPath = [NSString stringWithFormat:@\"%@/app/pygame-ios\", [[NSBundle mainBundle] bundlePath]];"
        )
        
        main_m_content = main_m_content.replace(
            "path = [NSString stringWithFormat:@\"%@/app\", resourcePath, nil];",
            "path = [NSString stringWithFormat:@\"%@/app/pygame-ios\", resourcePath, nil];"
        )

        with open(main_m_path, "w", encoding="utf-8") as f:
            f.write(main_m_content)
    else:
        print(f"Warning: Could not find {main_m_path}")

    # 4.5. Set App Icon
    print("Setting app icon...")
    icon_source = os.path.join(project_dir, "resources", "images", "icon.png")
    icon_dest_dir = os.path.join(template_dir, "pygame-ios", "Images.xcassets", "AppIcon.appiconset")
    if os.path.exists(icon_source) and os.path.exists(icon_dest_dir):
        icon_dest_path = os.path.join(icon_dest_dir, "clangen_icon.png")
        shutil.copy2(icon_source, icon_dest_path)
        
        # Upscale to 1024x1024 to satisfy actool validation
        run_cmd(["sips", "-z", "1024", "1024", icon_dest_path])
        
        # Update Contents.json to use the new icon
        contents_json_path = os.path.join(icon_dest_dir, "Contents.json")
        with open(contents_json_path, "r") as f:
            contents = json.load(f)
        
        contents["images"] = [
            {
                "filename": "clangen_icon.png",
                "idiom": "universal",
                "platform": "ios",
                "size": "1024x1024"
            }
        ]
        
        with open(contents_json_path, "w") as f:
            json.dump(contents, f, indent=2)
    else:
        print(f"Warning: Could not find icon source {icon_source} or destination {icon_dest_dir}")


    print("Exporting pip requirements...")
    requirements_path = os.path.join(project_dir, "requirements-ios.txt")
    
    # Generate requirements-ios.txt using uv
    run_cmd(["uv", "export", "--format", "requirements-txt", "--output-file", requirements_path])

    print("Skipping Pip Export to prevent macOS python 3.13 subprocess hang...")

    # Filter out C-extensions that are either incompatible or already provided by pygame-ios
    print("Filtering out incompatible C-extensions...")
    with open(requirements_path, "r", encoding="utf-8") as f:
        req_lines = f.readlines()
    
    with open(requirements_path, "w", encoding="utf-8") as f:
        for line in req_lines:
            # Parse the package name (ignoring version specifiers and environment markers)
            pkg_name = line.split("==")[0].split()[0].strip().lower() if line.strip() and not line.startswith("#") else ""
            
            # We skip pygame-ce/pygame (provided by template) and macOS C-extensions
            if pkg_name not in ["pygame-ce", "pygame", "ujson", "cryptography", "cffi", "pgpy", "pycparser", "-e"]:
                f.write(line)

    print("Installing requirements into app_packages.iphonesimulator and app_packages.iphoneos...")
    
    for platform in ["app_packages.iphonesimulator", "app_packages.iphoneos"]:
        app_packages_dir = os.path.join(template_dir, "pygame-ios", platform)
        os.makedirs(app_packages_dir, exist_ok=True)
        run_cmd([
            sys.executable, "-m", "pip", "install", 
            "--target", app_packages_dir, 
            "--no-deps",
            "-r", requirements_path
        ])
    
    # Clean up the generated requirements file
    if os.path.exists(requirements_path):
        os.remove(requirements_path)

    # 5. Build
    print(f"Building for {args.target}...")
    destination = "platform=iOS Simulator,name=IPad 10th Gen" if args.target == "simulator" else "generic/platform=iOS"
    
    xcodebuild_cmd = [
        "xcodebuild", "-project", os.path.join(template_dir, "pygame-ios.xcodeproj"),
        "-scheme", "pygame-ios",
        "-destination", destination,
        "build",
        "-derivedDataPath", os.path.join(template_dir, "build")
    ]
    
    run_cmd(xcodebuild_cmd)

    if args.target == "simulator":
        # 6. Install on Simulator
        print("Installing on Simulator...")
        run_cmd([
            "xcrun", "simctl", "install", "IPad 10th Gen",
            os.path.join(template_dir, "build", "Build", "Products", "Debug-iphonesimulator", "pygame-ios.app")
        ])

        # 7. Launch on Simulator
        print("Launching on Simulator...")
        run_cmd([
            "xcrun", "simctl", "launch", "IPad 10th Gen", BUNDLE_ID
        ])
        print("\n--- Build and Launch Complete! ---")
    else:
        print("\n--- Build Complete! ---")
        print("To run on a physical device, open the project in Xcode and deploy to your device.")


if __name__ == "__main__":
    main()
