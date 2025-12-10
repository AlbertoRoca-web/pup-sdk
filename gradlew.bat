@echo off
set DIR=%~dp0
set APP_BASE_NAME=%~n0
set DEFAULT_JVM_OPTS=-Xmx64m -Xms64m
set CLASSPATH=%DIR%\gradle\wrapper\gradle-wrapper.jar

if not exist "%CLASSPATH%" (
  echo Missing gradle-wrapper.jar. Please run "gradle wrapper" on a machine with Gradle installed.
  exit /b 1
)

java %DEFAULT_JVM_OPTS% -classpath "%CLASSPATH%" org.gradle.wrapper.GradleWrapperMain %*
