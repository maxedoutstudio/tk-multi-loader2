        

# Copyright (c) 2013 Shotgun Software Inc.
# 
# CONFIDENTIAL AND PROPRIETARY
# 
# This work is provided "AS IS" and subject to the Shotgun Pipeline Toolkit 
# Source Code License included in this distribution package. See LICENSE.
# By accessing, using, copying or modifying this work you indicate your 
# agreement to the Shotgun Pipeline Toolkit Source Code License. All rights 
# not expressly granted therein are reserved by Shotgun Software Inc.

"""
Hook that loads items into the current scene. 

This hook supports a number of different platforms and the behaviour on each platform is
different. See code comments for details.


"""
import tank
import os

class ExecuteLoadAction(tank.Hook):
    
    def execute(self, action_name, shotgun_data, **kwargs):
        """
        Hook entry point and app-specific code dispatcher
        """
                
        import nuke
        
        file_path = shotgun_data.get("path").get("local_path")
        
        # get the slashes right
        file_path = file_path.replace(os.path.sep, "/")

        (path, ext) = os.path.splitext(file_path)

        valid_extensions = [".png", ".jpg", ".jpeg", ".exr", ".cin", ".dpx", ".tiff", ".mov"]

        if ext in valid_extensions:
            # find the sequence range if it has one:
            seq_range = self._find_sequence_range(file_path)
            
            # create the read node
            if seq_range:
                nuke.nodes.Read(file=file_path, first=seq_range[0], last=seq_range[1])
            else:
                nuke.nodes.Read(file=file_path)
        else:
            self.parent.log_error("Unsupported file extension for %s - no read node will be created." % file_path)        

    def _find_sequence_range(self, path):
        """
        If the path contains a sequence then try to match it
        to a template and use that to extract the sequence range
        based on the files that exist on disk.
        """
        # find a template that matches the path:
        template = None
        try:
            template = self.parent.tank.template_from_path(path)
        except TankError, e:
            self.parent.log_error("Unable to find image sequence range!")
        if not template:
            return
            
        # get the fields and find all matching files:
        fields = template.get_fields(path)
        if not "SEQ" in fields:
            return
        files = self.parent.tank.paths_from_template(template, fields, ["SEQ", "eye"])
        
        # find frame numbers from these files:
        frames = []
        for file in files:
            fields = template.get_fields(file)
            frame = fields.get("SEQ")
            if frame != None:
                frames.append(frame)
        if not frames:
            return
        
        # return the range
        return (min(frames), max(frames))

