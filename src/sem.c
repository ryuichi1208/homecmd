

#include    <stdio.h>
#include    <sys/types.h>
#include    <sys/ipc.h>
#include    <sys/sem.h>
#define SZ_BUF  128

union semun  {
    int   val;
    struct semid_ds *buf;
    ushort *array;
}   c_arg;               /* semaphore  control info   */
    
int sem_get(char *path) {
    int   sid;

    if ((sid=semget(ftok(path,0),1,0666|IPC_CREAT))== -1) {
        die_err("semget");
    }

    if (semctl(sid,0,GETVAL,c_arg)==0) {
        c_arg.val=1;
        if (semctl(sid,0,SETVAL,c_arg)==-1) {
            die_err("semctl");
        }
    } 
    else  die_err("semctl");
    return(sid);
}
    
int sem_lock(int sid) {
    struct sembuf  sb;
    
    sb.sem_num=0;
    sb.sem_op=-1;
    sb.sem_flg=0;
    if (semop(sid,&sb,1)== -1) {
        die_err("semop");
    }
    return(1);
}
    
int sem_unlock(int sid) {
    struct sembuf  sb;
    
    sb.sem_num=0;
    sb.sem_op=1;
    sb.sem_flg=0;
    if (semop(sid,&sb,1)== -1) {
        die_err("semop");
    }
    return(1);
}
    
int main() {
    int   sid,ret;
    char  buf[SZ_BUF];
    
    setbuf(stdout,NULL);

    if ((sid=sem_get("/tmp/aaa"))==-1) {
        exit(-1);
    }
    printf("sid=%d\n",sid);
    
    while(1){
        ret  = semctl(sid,0,GETVAL,c_arg);
        printf("<%d> [L]ock / [U]nlock : ",ret);
        if (fgets(buf,SZ_BUF,stdin) != NULL) {
            if (tolower(buf[0])=='l') {
                ret = sem_lock(sid);
                printf("sem_lock()=%d\n",ret);
            }
            else if (tolower(buf[0])=='u') {
                ret = sem_unlock(sid);
                printf("sem_unlock()=%d\n",ret);
            }
        }
    }
}
