FROM public.ecr.aws/lambda/python:3.12

# Install Playwright system dependencies
RUN dnf install -y \
    atk \
    cups-libs \
    gtk3 \
    libXcomposite \
    alsa-lib \
    libXcursor \
    libXdamage \
    libXext \
    libXi \
    libXrandr \
    libXScrnSaver \
    libXtst \
    pango \
    at-spi2-atk \
    libXt \
    xorg-x11-server-Xvfb \
    xorg-x11-xauth \
    dbus-glib \
    dbus-glib-devel \
    nss \
    mesa-libgbm \
    && dnf clean all

# Copy requirements and install Python dependencies
COPY requirements.txt ${LAMBDA_TASK_ROOT}/
RUN pip install --no-cache-dir -r ${LAMBDA_TASK_ROOT}/requirements.txt

# Set Playwright browsers path to a location accessible to Lambda runtime
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/playwright

# Install Playwright Chromium browser to the custom path
RUN playwright install chromium
# Note: Dependencies already installed via dnf above, no need for install-deps

# Copy application code directly to task root (not in subdirectory)
COPY src/*.py ${LAMBDA_TASK_ROOT}/

# Fix file permissions for Lambda runtime
RUN chmod 644 ${LAMBDA_TASK_ROOT}/*.py

# Set Lambda handler
CMD ["lambda_handler.lambda_handler"]
