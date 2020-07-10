import logging
import shlex

import mustup.core.format
import mustup.core.tup.rule

logger = logging.getLogger(
    __name__,
)


class Format(
            mustup.core.format.Format,
        ):
    supported_extensions = {
        '.wave',
    }

    supported_transformations = {
    }

    # opusenc offers shortcuts for some common tags
    tag_parameter_map = {
        'album': '--album',
        'artist': '--artist',
        'title': '--title',
        'track number': '--tracknumber',
    }

    # opusenc offers shortcuts for some Vorbis comments
    vorbiscomment_parameter_map = {
        'DATE': '--date',
    }

    def process(
                self,
                metadata,
                source_basename,
                source_name,
                transformations,
            ):
        output_name = f'{ source_basename }.opus'

        command = [
            'opusenc',
            '@(OPUSENC_FLAGS)',
        ]

        try:
            tags = metadata['tags']
        except KeyError:
            pass
        else:
            # Tags are sorted to ensure consistent ordering of the command line arguments.
            # If ordering varied, tup would run the commands again.

            try:
                common_tags = tags['common']
            except KeyError:
                pass
            else:
                iterator = Format.tag_parameter_map.items(
                )

                sorted_pairs = sorted(
                    iterator,
                )

                for pair in sorted_pairs:
                    tag_key = pair[0]
                    parameter = pair[1]
                    try:
                        vorbis_comment_value = common_tags[tag_key]
                    except KeyError:
                        pass
                    else:
                        command.append(
                            parameter,
                        )

                        argument = shlex.quote(
                            vorbis_comment_value,
                        )

                        command.append(
                            argument,
                        )

            try:
                vorbis_comments = tags['Vorbis']
            except KeyError:
                pass
            else:
                iterator = vorbis_comments.items(
                )

                sorted_pairs = sorted(
                    iterator,
                )

                for pair in sorted_pairs:
                    vorbis_comment_key = pair[0]
                    vorbis_comment_value = pair[1]

                    try:
                        parameter = Format.vorbiscomment_parameter_map[vorbis_comment_key]
                    except KeyError:
                        parameter = '--comment'

                        argument = shlex.quote(
                            f'{ vorbis_comment_key }={ vorbis_comment_value }',
                        )
                    else:
                        argument = shlex.quote(
                            vorbis_comment_value,
                        )

                    command.append(
                        parameter,
                    )

                    command.append(
                        argument,
                    )

        try:
            pictures = metadata['pictures']['APIC']
        except KeyError:
            pass
        else:
            iterator = pictures.items(
            )

            sorted_pairs = sorted(
                iterator,
            )

            for pair in sorted_pairs:
                picture_type = pair[0]
                picture_details = pair[1]
                path = picture_details['path']
                description = picture_details.get(
                    'description',
                    '',
                )

                command.append(
                    '--picture',
                )

                parts = [
                    str(
                        picture_type,
                    ),
                    '',
                    description,
                    '',
                    path,
                ]

                picture_specification = '|'.join(
                    parts,
                )

                argument = shlex.quote(
                    picture_specification,
                )

                command.append(
                    argument,
                )

        command.extend(
            [
                '--',
                shlex.quote(
                    source_name,
                ),
                shlex.quote(
                    output_name,
                ),
            ],
        )

        rule = mustup.core.tup.rule.Rule(
            inputs=[
                source_name,
            ],
            command=command,
            outputs=[
                output_name,
            ],
        )

        return rule
