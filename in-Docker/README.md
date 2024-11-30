
# Gradle Project Dockerfile Generator

This script automates the creation of a `Dockerfile` for Gradle projects, including Android SDK installation and necessary dependencies. It also allows for building and tagging Docker images locally.

---

## **Features**
- Automatically detects Java and Gradle versions from the project files.
- Recursively scans for `build.gradle` and `build.gradle.kts` files to gather dependencies.
- Installs the Android SDK (`platform-tools`, `build-tools`, and platforms).
- Generates a `Dockerfile` tailored for the Gradle project.
- Optionally builds and tags the Docker image in your local Docker environment.

---

## **Requirements**
- Python 3.6 or higher.
- Docker installed and running.
- A Gradle project with valid `build.gradle` or `build.gradle.kts` files.

---

## **Setup**
1. Clone the repository:
   ```bash
   git clone <repository_url>
   cd <repository_directory>
   ```
2. Make sure Docker is properly installed and running on your machine.

---

## **Usage**
1. Run the script:
   ```bash
   python generate_dockerfile_and_build.py
   ```
2. Follow the prompts:
   - Provide the path to your Gradle project.
   - Review the extracted information about the project.
   - Let the script generate a `Dockerfile`.
   - Optionally, provide a Docker image name to build and tag the image locally.

---

## **Example Workflow**
### **Running the Script**
```bash
python generate_dockerfile_and_build.py
```

### **Output Example**
```
Enter the path to the Gradle project: /path/to/project

Project information found:
- Java Version: 11
- Gradle Version: 7.4
- Dependencies:
  - implementation 'com.google.guava:guava:30.1.1-jre'
  - implementation 'org.springframework:spring-core:5.3.8'

Generating Dockerfile with the following settings:
- Java Version: 11
- Gradle Version: 7.4
- Found Dependencies:
  - implementation 'com.google.guava:guava:30.1.1-jre'
  - implementation 'org.springframework:spring-core:5.3.8'

Dockerfile successfully generated: Dockerfile

Enter the name for the Docker image (e.g., my-project:latest): my-project:latest

Building Docker image 'my-project:latest'...
Image successfully built and tagged as 'my-project:latest'
```

### **Generated Dockerfile**
```dockerfile
# Base image with Java 11
FROM gradle:7.4-jdk11

# Set environment variables
ENV ANDROID_SDK_ROOT /opt/android-sdk
ENV PATH $ANDROID_SDK_ROOT/cmdline-tools/tools/bin:$ANDROID_SDK_ROOT/platform-tools:$PATH

# Install required dependencies
RUN mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && apt-get update && apt-get install -y --no-install-recommends     wget unzip lib32stdc++6 lib32z1 &&     wget https://dl.google.com/android/repository/commandlinetools-linux-8512546_latest.zip -O /cmdline-tools.zip &&     unzip /cmdline-tools.zip -d $ANDROID_SDK_ROOT/cmdline-tools &&     mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/tools &&     rm /cmdline-tools.zip &&     yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager --licenses || true &&     yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager "platform-tools" "platforms;android-32" --verbose || true &&     yes | $ANDROID_SDK_ROOT/cmdline-tools/tools/bin/sdkmanager "build-tools;32.0.0" --verbose || true

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Preload Gradle dependencies
RUN ./gradlew dependencies --refresh-dependencies

# Default command to build the project
CMD ["./gradlew", "assemble"]
```

---

## **Troubleshooting**
### Common Issues
- **"The specified path does not exist"**: Verify the project path you entered.
- **Docker-related errors**: Ensure Docker is installed, running, and that you have the necessary permissions.

---

## **Contributing**
Contributions are welcome! Fork the repository, submit issues, or create pull requests to improve the script.

---

## **License**
This project is licensed under the MIT License. See the LICENSE file for details.
