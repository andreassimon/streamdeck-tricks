import logging
import pulsectl

logger = logging.getLogger('streamdeck-tricks')


def configure_pulse():
    def sink_input_move(sink_inputs, sinks):
        for si in sink_inputs:
            for s in sinks:
                logger.debug("MOVE sink input [{}] to [{}]".format(si, s))
                pulse.sink_input_move(si.index, s.index)

    def source_output_move(source_outputs, sources):
        for so in source_outputs:
            for s in sources:
                logger.debug("MOVE source output [{}] to [{}]".format(so, s))
                pulse.source_output_move(so.index, s.index)

    with pulsectl.Pulse('streamdeck-tricks') as pulse:
        yeti = list(filter(lambda si: si.name == 'Yeti', pulse.sink_input_list()))
        teams_sink = list(filter(lambda s: s.name == 'teams_sink', pulse.sink_list()))
        monitored_teams_sink = list(filter(lambda s: s.name == 'monitored_teams_sink', pulse.sink_list()))

        sink_input_move(yeti, teams_sink)

        def is_obs_monitor(si):
            return (si.name != 'Yeti') and ('application.name' in si.proplist) and (
                    si.proplist['application.name'] == 'OBS')

        def is_teams_input(so):
            return ('application.name' in so.proplist) and (so.proplist['application.name'] == 'Skype')

        def is_teams_output(si):
            return ('application.name' in si.proplist) and (si.proplist['application.name'] == 'Skype')

        obs_monitors = list(filter(is_obs_monitor, pulse.sink_input_list()))
        sink_input_move(obs_monitors, monitored_teams_sink)

        def is_jabra_link_370_sink(si):
            return ('alsa.card_name' in si.proplist) and (si.proplist['alsa.card_name'] == 'Jabra Link 370')

        teams_output = list(filter(is_teams_output, pulse.sink_input_list()))
        jabra_link_370_sink = list(filter(is_jabra_link_370_sink, pulse.sink_list()))

        sink_input_move(teams_output, jabra_link_370_sink)

        skype_input = list(filter(is_teams_input, pulse.source_output_list()))
        teams_mic = list(filter(lambda s: s.name == 'teams_mic', pulse.source_list()))
        source_output_move(skype_input, teams_mic)
