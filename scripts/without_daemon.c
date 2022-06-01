#include <sys/types.h>
#include <sys/stat.h>
#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <errno.h>
#include <unistd.h>
#include <syslog.h>
#include <string.h>
#include <stdbool.h>
#include <fcntl.h>
#include <poll.h>

#include <linux/uinput.h>

#define DAEMON_NAME "xenon_multimedia_keys"

#define DEBUG 0
#define CREATE_DAMEON 0

#define DAEMON_DEBUG(fmt, args...) \
    if (DEBUG) \
        printf(" [debug] %s(%d): " fmt "\n", \
                __FUNCTION__, __LINE__, ## args)

void emit(int fd, int type, int code, int val)
{
   struct input_event ie;

   ie.type = type;
   ie.code = code;
   ie.value = val;
   /* timestamp values below are ignored */
   ie.time.tv_sec = 0;
   ie.time.tv_usec = 0;

   write(fd, &ie, sizeof(ie));
}

void click(int fd, int code)
{
    emit(fd, EV_KEY, code, 1);
    emit(fd, EV_SYN, SYN_REPORT, 0);
    emit(fd, EV_KEY, code, 0);
    emit(fd, EV_SYN, SYN_REPORT, 0);
    usleep(10*1000); // sleep 10 miliseconds
}

int main(int argc, char *argv[]) {

    // ----------- init ------------
    
    FILE *fp;
    char command_output[8];
    char* event_file_name;

    /* Open the command for reading. */
    fp = popen("cat /proc/bus/input/devices | grep -A4 \"SINOWEALTH Game Mouse Keyboard\" | awk \'/Handlers/{print $4}\'", "r");
    if (fp == NULL) {
        DAEMON_DEBUG("Failed to run command");
        exit(1);
    }

    /* Read the output a line at a time - output it. */
    fgets(command_output, sizeof(command_output), fp);
    DAEMON_DEBUG("%s", command_output);

    /* close */
    pclose(fp);

    char c;
    size_t index = 0;

    do {
        c = command_output[index];
        index++;
    } while(c != '\n');

    command_output[index-1] = '\0';
    event_file_name = command_output;
    DAEMON_DEBUG("index:%li\n", index);

    struct uinput_setup usetup;

    int fd = open("/dev/uinput", O_WRONLY | O_NONBLOCK);

    ioctl(fd, UI_SET_EVBIT, EV_KEY);
    ioctl(fd, UI_SET_KEYBIT, KEY_PLAYPAUSE);
    ioctl(fd, UI_SET_KEYBIT, KEY_MUTE);
    ioctl(fd, UI_SET_KEYBIT, KEY_NEXT);
    ioctl(fd, UI_SET_KEYBIT, KEY_PREVIOUS);
    ioctl(fd, UI_SET_KEYBIT, KEY_MUTE);
    ioctl(fd, UI_SET_KEYBIT, KEY_VOLUMEUP);
    ioctl(fd, UI_SET_KEYBIT, KEY_VOLUMEDOWN);
    ioctl(fd, UI_SET_KEYBIT, KEY_CALC);
    ioctl(fd, UI_SET_KEYBIT, KEY_HOMEPAGE);

    memset(&usetup, 0, sizeof(usetup));
    usetup.id.bustype = BUS_USB;
    usetup.id.vendor = 0x1234; /* sample vendor */
    usetup.id.product = 0x5678; /* sample product */
    strcpy(usetup.name, "Example device");

    ioctl(fd, UI_DEV_SETUP, &usetup);
    ioctl(fd, UI_DEV_CREATE);
    
    // reading
    
    char input_dev[] = "/dev/input/";

    char* full_path = (char*)malloc(strlen(input_dev) + strlen(event_file_name)+1);
    strcpy(full_path, input_dev);
    strcat(full_path, event_file_name);

    DAEMON_DEBUG("full path is: %s\n", full_path);

    int timeout_ms = 5000;
    int st;
    int ret;
    struct pollfd fds[1];

    fds[0].fd = open(full_path, O_RDONLY|O_NONBLOCK);

    if(fds[0].fd<0)
    {
        DAEMON_DEBUG("error unable open for reading '%s'\n", full_path);
        return(0);
    }

    const int input_size = 4096;
    unsigned char input_data[input_size];
    memset(input_data,0,input_size);

    fds[0].events = POLLIN;

    // --------
    // daemon
    // --------
#if CREATE_DAMEON
    // set logging mask and open the log
    setlogmask(LOG_UPTO(LOG_NOTICE));
    openlog(DAEMON_NAME, LOG_CONS | LOG_NDELAY | LOG_PERROR | LOG_PID, LOG_USER);

    syslog(LOG_INFO, "Entering Daemon");

    pid_t pid, sid;

   // fork the parent Process
    pid = fork();

    if (pid < 0) { exit(EXIT_FAILURE); }

    // kill the parent process
    if (pid > 0) { exit(EXIT_SUCCESS); }

    // change file mask
    umask(0);

    // create a new signature id for child
    sid = setsid();
    if (sid < 0) { exit(EXIT_FAILURE); }

    // change directory
    if ((chdir("/")) < 0) { exit(EXIT_FAILURE); }

    // close standard file descriptors
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
#endif
    printf("AAAAAAAAAAAAAAAAAA");
    //----------------
    // Main Process
    //----------------
    while(true) {
        ret = poll(fds, 1, timeout_ms);

        if(ret>0)
        {
            if(fds[0].revents)
            {
                ssize_t r = read(fds[0].fd,input_data,input_size);

                if(r<0)
                {
                    DAEMON_DEBUG("error %d\n",(int)r);
                    break;
                }
                else
                {
                    DAEMON_DEBUG("total bytes read %d/%d\n",(int)r,input_size);

                    for(int i = 0; i<r;i++)
                    {
                        if (i % 16 == 0 && i != 0) {
                            DAEMON_DEBUG("\n");
                        }
                        DAEMON_DEBUG("%02X ",(unsigned char)input_data[i]);
                    }
                    if ((unsigned char)input_data[44] == 0x01) {
                        unsigned char expr = (unsigned char)input_data[20];
                        switch (expr) {
                            case 0xa0:
                                click(fd, KEY_PLAYPAUSE);
                                DAEMON_DEBUG("CLICKED KEY_PLAYPAUSE");
                                break;
                            case 0xa1:
                                click(fd, KEY_NEXT);
                                DAEMON_DEBUG("CLICKED KEY_NEXT");
                                break;
                            case 0xa2:
                                click(fd, KEY_PREVIOUS);
                                DAEMON_DEBUG("CLICKED KEY_PREVIOUS");
                                break;
                            case 0xa3:
                                click(fd, KEY_STOP);
                                DAEMON_DEBUG("CLICKED KEY_STOP");
                                break;
                            case 0xa4:
                                click(fd, KEY_MUTE);
                                DAEMON_DEBUG("CLICKED KEY_MUTE");
                                break;
                            case 0xa5:
                                click(fd, KEY_VOLUMEUP);
                                DAEMON_DEBUG("CLICKED KEY_VOLUMEUP");
                                break;
                            case 0xa6:
                                click(fd, KEY_VOLUMEDOWN);
                                DAEMON_DEBUG("CLICKED KEY_VOLUMEDOWN");
                                break;
                            case 0xa8:
                                click(fd, KEY_CALC);
                                DAEMON_DEBUG("CLICKED KEY_CALCULATOR");
                                break;
                            case 0xaa:
                                click(fd, KEY_HOMEPAGE);
                                DAEMON_DEBUG("CLICKED KEY_HOMEPAGE");
                                break;
                        }
                    }

                    DAEMON_DEBUG("\n");
                    memset(input_data,0,input_size);
                }
            }
            else
            {
                DAEMON_DEBUG("error\n");
            }
        }
        else
        {
            DAEMON_DEBUG("timeout\n");
        }
    }

    // close driver
    ioctl(fd, UI_DEV_DESTROY);
    close(fd);
    close(fds[0].fd);

    // close the log
    closelog();
}
