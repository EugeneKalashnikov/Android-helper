import os
import re
import subprocess


def find_gradle_files(project_path):
    """
    Recursively searches for all build.gradle and build.gradle.kts files in the project.
    """
    gradle_files = []
    for root, _, files in os.walk(project_path):
        for file in files:
            if file in ["build.gradle", "build.gradle.kts"]:
                gradle_files.append(os.path.join(root, file))
    return gradle_files


def extract_gradle_info(project_path):
    """
    Analyzes the Gradle project to extract information about Java, Gradle, and dependencies.
    """
    gradle_wrapper_path = os.path.join(project_path, "gradle", "wrapper", "gradle-wrapper.properties")
    gradle_files = find_gradle_files(project_path)

    java_version = None
    gradle_version = None
    dependencies = []

    # Analyze all found Gradle files
    for gradle_file in gradle_files:
        with open(gradle_file, "r") as file:
            for line in file:
                # Search for Java version
                java_match = re.search(r"java\s*\(\s*version\s*=\s*['\"](\d+)['\"]\)", line)
                if java_match and not java_version:
                    java_version = java_match.group(1)

                # Search for dependencies
                dependency_match = re.search(r"(implementation|api|compileOnly|runtimeOnly)\s*['\"](.+?):(.+?):(.+?)['\"]", line)
                if dependency_match:
                    dependencies.append(dependency_match.group(0))

    # Analyze gradle-wrapper.properties for the Gradle version
    if os.path.exists(gradle_wrapper_path):
        with open(gradle_wrapper_path, "r") as file:
            for line in file:
                gradle_match = re.search(r"gradle-(\d+\.\d+\.\d+)-all.zip", line)
                if gradle_match:
                    gradle_version = gradle_match.group(1)

    return {
        "java_version": java_version or "11",
        "gradle_version": gradle_version or "7.0",
        "dependencies": dependencies
    }


def generate_dockerfile(gradle_info, output_path="Dockerfile"):
    """
    Generates a Dockerfile based on project information.
    """
    java_version = gradle_info["java_version"]
    gradle_version = gradle_info["gradle_version"]

    print("\nGenerating Dockerfile with the following settings:")
    print(f"- Java Version: {java_version}")
    print(f"- Gradle Version: {gradle_version}")
    if gradle_info["dependencies"]:
        print("- Found Dependencies:")
        for dep in gradle_info["dependencies"]:
            print(f"  - {dep}")
    else:
        print("- No dependencies found.")

    dockerfile_content = f"""
    # Base image with Java {java_version}
    FROM gradle:{gradle_version}-jdk{java_version}

    # Set environment variables
    ENV ANDROID_SDK_ROOT /opt/android-sdk
    ENV PATH $ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH

    # Install required dependencies
    RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && apt-get update && apt-get install -y --no-install-recommends \\
        wget unzip lib32stdc++6 lib32z1 && \\
        wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O /cmdline-tools.zip && \\
        unzip /cmdline-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools && \\
        mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/tools && \\
        rm /cmdline-tools.zip && \\
        yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager --licenses || true && \\
        yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager "platform-tools" "platforms;android-32" --verbose || true && \\
        yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager "build-tools;32.0.0" --verbose || true

    # Set working directory
    WORKDIR /app

    # Copy project files
    COPY . .

    # Preload Gradle dependencies
    RUN ./gradlew dependencies --refresh-dependencies

    # Default command to build the project
    CMD ["./gradlew", "assemble"]
    """

    with open(output_path, "w") as file:
        file.write(dockerfile_content.strip())

    print(f"\nDockerfile successfully generated: {output_path}")


def build_and_tag_image(project_path, image_name):
    """
    Builds a Docker image and tags it in the local repository.
    """
    try:
        print(f"\nBuilding Docker image '{image_name}'...")
        subprocess.run(["docker", "build", "-t", image_name, project_path], check=True)
        print(f"Image successfully built and tagged as '{image_name}'")
    except subprocess.CalledProcessError as e:
        print(f"Error building Docker image: {e}")
        exit(1)


if __name__ == "__main__":
    project_path = input("Enter the path to the Gradle project: ").strip()
    if not os.path.exists(project_path):
        print("The specified path does not exist!")
    else:
        gradle_info = extract_gradle_info(project_path)
        print("\nProject information found:")
        print(f"- Java Version: {gradle_info['java_version']}")
        print(f"- Gradle Version: {gradle_info['gradle_version']}")
        print("- Dependencies:")
        if gradle_info["dependencies"]:
            for dep in gradle_info["dependencies"]:
                print(f"  - {dep}")
        else:
            print("  - No dependencies found.")
        
        generate_dockerfile(gradle_info)
        
        # Request Docker image name
        image_name = input("\nEnter the name for the Docker image (e.g., my-project:latest): ").strip()
        if image_name:
            build_and_tag_image(project_path, image_name)
        else:
            print("Image name not specified, skipping the build.")
