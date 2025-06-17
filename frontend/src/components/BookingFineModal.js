const modalStyle = {
    position: 'absolute',
    top: '50%',
    left: '50%',
    transform: 'translate(-50%, -50%)',
    width: 400,
    bgcolor: 'background.paper',
    boxShadow: 24,
    p: 4,
    borderRadius: 2,
};

const buttonStyle = {
    mt: 2,
    mr: 1,
    backgroundColor: '#42b983',
    color: 'white',
    '&:hover': {
        backgroundColor: '#3a9f74',
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 8px rgba(0, 0, 0, 0.2)',
    },
    transition: 'all 0.3s ease',
    borderRadius: '6px',
    padding: '0.7rem 1.2rem',
    border: 'none',
    cursor: 'pointer',
};

const cancelButtonStyle = {
    mt: 2,
    mr: 1,
    backgroundColor: '#ff7675',
    color: 'white',
    '&:hover': {
        backgroundColor: '#d63031',
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 15px rgba(255, 118, 117, 0.4)',
    },
    transition: 'all 0.3s ease',
    borderRadius: '6px',
    padding: '0.7rem 1.2rem',
    border: 'none',
    cursor: 'pointer',
};

<Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
    <Button 
        onClick={handleClose} 
        sx={cancelButtonStyle}
    >
        Отмена
    </Button>
    <Button 
        onClick={handleSave} 
        sx={buttonStyle}
    >
        Добавить
    </Button>
</Box> 