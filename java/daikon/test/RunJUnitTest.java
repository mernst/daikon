// From https://www.baeldung.com/junit-tests-run-programmatically-from-java

public class RunJUnitTestClass {

  SummaryGeneratingListener listener = new SummaryGeneratingListener();

  public void runOne(Class<?> testClass) {
    LauncherDiscoveryRequest request =
        LauncherDiscoveryRequestBuilder.request().selectors(selectClass(testClass)).build();
    Launcher launcher = LauncherFactory.create();
    TestPlan testPlan = launcher.discover(request);
    launcher.registerTestExecutionListeners(listener);
    launcher.execute(request);
  }
}
