from nornir import InitNornir


class NutsContext:
    def __init__(self, nuts_parameters):
        self.nuts_parameters = nuts_parameters


class NornirNutsContext(NutsContext):
    def __init__(self, nuts_parameters):
        super().__init__(nuts_parameters)
        self._transformed_result = None

    def nuts_task(self):
        raise NotImplementedError

    def nuts_arguments(self):
        return {}

    def transform_result(self, general_result):
        return general_result

    def nornir_filter(self):
        return None

    def nornir_config_file(self):
        return "nr-config.yaml"

    def initialized_nornir(self):
        config_file = self.nornir_config_file()
        return InitNornir(config_file=config_file, logging=False)

    def general_result(self):
        nuts_task = self.nuts_task()
        nuts_arguments = self.nuts_arguments()
        nornir_filter = self.nornir_filter()
        initialized_nornir = self.initialized_nornir()

        if nornir_filter:
            selected_hosts = initialized_nornir.filter(nornir_filter)
        else:
            selected_hosts = initialized_nornir
        overall_results = selected_hosts.run(task=nuts_task, **nuts_arguments)
        return overall_results

    @property
    def transformed_result(self):
        if not self._transformed_result:
            self._transformed_result = self.transform_result(self.general_result())
        return self._transformed_result
